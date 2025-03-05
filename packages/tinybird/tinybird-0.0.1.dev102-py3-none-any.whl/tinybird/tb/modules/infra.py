import json
import subprocess
import time
import uuid
from pathlib import Path
from typing import Optional

import click
import pyperclip
import requests
from click import Context

from tinybird.client import TinyB
from tinybird.syncasync import async_to_sync
from tinybird.tb.modules.cli import CLIException, cli
from tinybird.tb.modules.common import coro, echo_safe_humanfriendly_tables_format_smart_table
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.feedback_manager import FeedbackManager

from .common import CONTEXT_SETTINGS

K8S_YML = """
---
apiVersion: v1
kind: Namespace
metadata:
  name: %(namespace)s
  labels:
    name: tinybird
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tinybird
  namespace:  %(namespace)s
  labels:
    name: tinybird
automountServiceAccountToken: true
---
apiVersion: v1
kind: Service
metadata:
  name: tinybird
  namespace:  %(namespace)s
  labels:
    name: tinybird
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    name: tinybird
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  namespace: %(namespace)s
  name: tinybird
  annotations:
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS13-1-2-2021-06
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/target-type: 'ip'
    alb.ingress.kubernetes.io/load-balancer-name: %(namespace)s
    alb.ingress.kubernetes.io/success-codes: '200,301,302'
spec:
  ingressClassName: alb
  tls:
    - hosts:
        - %(full_dns_name)s
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: tinybird
                port:
                  name: http
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: tinybird
  namespace: %(namespace)s
spec:
  serviceName: "tinybird"
  replicas: 1
  selector:
    matchLabels:
      name: tinybird
  template:
    metadata:
      labels:
        name: tinybird
    spec:
      serviceAccountName: tinybird
      containers:
        - name: tinybird
          image: "tinybirdco/tinybird-local:beta"
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 7181
              protocol: TCP
          env:
            - name: TB_INFRA_TOKEN
              value: "%(infra_token)s"
            - name: TB_INFRA_WORKSPACE
              value: "%(infra_workspace)s"
            - name: TB_INFRA_ORGANIZATION
              value: "%(infra_organization)s"
            - name: TB_INFRA_USER
              value: "%(infra_user)s"
          volumeMounts:
          - name: clickhouse-data
            mountPath: /var/lib/clickhouse
  volumeClaimTemplates:
  - metadata:
      name: clickhouse-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi
      storageClassName: %(storage_class)s
"""

TERRAFORM_FIRST_TEMPLATE = """
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "%(aws_region)s"
}

# Get the hosted zone data
data "aws_route53_zone" "selected" {
  name = "%(dns_zone_name)s"
}

# Create ACM certificate
resource "aws_acm_certificate" "cert" {
  domain_name               = "%(dns_record)s.${data.aws_route53_zone.selected.name}"
  validation_method         = "DNS"
  subject_alternative_names = [data.aws_route53_zone.selected.name]

  lifecycle {
    create_before_destroy = true
  }
}

# Create DNS records for certificate validation
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.selected.zone_id
}

# Certificate validation
resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}
"""

TERRAFORM_SECOND_TEMPLATE = """
# Create Route 53 record for the load balancer
data "aws_alb" "tinybird" {
  name = "%(namespace)s"
}

resource "aws_route53_record" "tinybird" {
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = "%(full_dns_name)s"
  type    = "A"
  alias {
    name                   = data.aws_alb.tinybird.dns_name
    zone_id                = data.aws_alb.tinybird.zone_id
    evaluate_target_health = true
  }
}

output "tinybird_dns" {
  description = "The DNS name for Tinybird"
  value       = aws_route53_record.tinybird.fqdn
}
"""


@cli.group(context_settings=CONTEXT_SETTINGS, hidden=True)
@click.pass_context
def infra(ctx: Context) -> None:
    """Infra commands."""


@infra.command(name="init")
@click.option("--name", type=str, help="Name for identifying the self-managed infrastructure in Tinybird")
@click.option("--provider", type=str, help="Infrastructure provider. Possible values are: aws, gcp, azure)")
@click.option("--region", type=str, help="AWS region, when using aws as the provider")
@click.option("--dns-zone-name", type=str, help="DNS zone name")
@click.option("--namespace", type=str, help="Kubernetes namespace for the deployment")
@click.option("--dns-record", type=str, help="DNS record name to create, without domain. For example, 'tinybird')")
@click.option("--storage-class", type=str, help="Storage class for the k8s StatefulSet")
@click.option(
    "--auto-apply", is_flag=True, help="Automatically apply Terraform and kubectl configuration without prompting"
)
@click.option("--skip-apply", is_flag=True, help="Skip Terraform and kubectl configuration and application")
@click.pass_context
def infra_init(
    ctx: Context,
    name: str,
    provider: str,
    region: Optional[str] = None,
    dns_zone_name: Optional[str] = None,
    namespace: Optional[str] = None,
    dns_record: Optional[str] = None,
    storage_class: Optional[str] = None,
    auto_apply: bool = False,
    skip_apply: bool = False,
) -> None:
    """Init infra"""
    # Check if provider is specified
    if not provider:
        click.echo("Error: --provider option is required. Specify a provider. Possible values are: aws, gcp, azure.")
        return

    # AWS-specific Terraform template creation
    if provider.lower() != "aws":
        click.echo("Provider not supported yet.")
        return

    # Create infra directory if it doesn't exist
    infra_dir = Path(f"infra/{provider}")
    infra_dir.mkdir(exist_ok=True)
    yaml_path = infra_dir / "k8s.yaml"
    tf_path = infra_dir / "main.tf"
    config_path = infra_dir / "config.json"

    # Load existing configuration if available
    config = {}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            click.echo("Loaded existing configuration from config.json")
        except json.JSONDecodeError:
            click.echo("Warning: Could not parse existing config.json. Creating a new file...")

    # Generate a random ID for default values
    random_id = str(uuid.uuid4())[:8]

    # Get or prompt for configuration values
    name = name or click.prompt("Enter the name for your self-managed region", type=str)
    region = region or config.get("region") or click.prompt("Enter the AWS region", default="us-east-1", type=str)
    dns_zone_name = dns_zone_name or config.get("dns_zone_name") or click.prompt("Enter the DNS zone name", type=str)
    namespace = (
        namespace
        or config.get("namespace")
        or click.prompt("Enter the Kubernetes namespace", default=f"tinybird-{random_id}", type=str)
    )
    dns_record = (
        dns_record
        or config.get("dns_record")
        or click.prompt("Enter the DNS record name, without domain", default=f"tinybird-{random_id}", type=str)
    )
    storage_class = config.get("storage_class") or click.prompt(
        "Enter the Kubernetes storage class", default="gp3-encrypted", type=str
    )

    # Save configuration
    config = {
        "provider": provider,
        "region": region,
        "dns_zone_name": dns_zone_name,
        "namespace": namespace,
        "dns_record": dns_record,
        "storage_class": storage_class,
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    click.echo(f"Configuration saved to {config_path}")

    client: TinyB = ctx.obj["client"]
    cli_config = CLIConfig.get_project_config()
    user_client = cli_config.get_client(token=cli_config.get_user_token() or "")
    user_workspaces = async_to_sync(user_client.user_workspaces_with_organization)()
    admin_org_id = user_workspaces.get("organization_id")
    admin_org_name = user_workspaces.get("organization_name", "")
    infras = async_to_sync(client.infra_list)(organization_id=admin_org_id)
    infra = next((infra for infra in infras if infra["name"] == name), None)
    if not infra:
        click.echo(FeedbackManager.highlight(message=f"\n» Creating infrastructure '{name}' in Tinybird..."))
        host = f"https://{dns_record}.{dns_zone_name}"
        infra = async_to_sync(client.infra_create)(organization_id=admin_org_id, name=name, host=host)

    infra_token = infra["token"]

    # Write the Terraform template
    terraform_content = TERRAFORM_FIRST_TEMPLATE % {
        "aws_region": region,
        "dns_zone_name": dns_zone_name,
        "dns_record": dns_record,
    }

    with open(tf_path, "w") as f:
        f.write(terraform_content.lstrip())

    click.echo(f"Created Terraform configuration in {tf_path}")

    new_content = K8S_YML % {
        "namespace": namespace,
        "storage_class": storage_class,
        "full_dns_name": f"{dns_record}.{dns_zone_name}",
        "infra_token": infra_token,
        "infra_workspace": cli_config.get("name", ""),
        "infra_organization": admin_org_name,
        "infra_user": cli_config.get_user_email() or "",
    }

    with open(yaml_path, "w") as f:
        f.write(new_content.lstrip())

    click.echo(f"Created Kubernetes configuration in {yaml_path}")

    # Apply Terraform configuration if user confirms
    if not skip_apply:
        # Initialize Terraform
        click.echo("Initializing Terraform...")
        init_result = subprocess.run(["terraform", f"-chdir={infra_dir}", "init"], capture_output=True, text=True)

        if init_result.returncode != 0:
            click.echo("Terraform initialization failed:")
            click.echo(init_result.stderr)
            return

        # Run terraform plan first
        click.echo("\nRunning Terraform plan...\n")
        plan_result = subprocess.run(["terraform", f"-chdir={infra_dir}", "plan"], capture_output=True, text=True)

        if plan_result.returncode != 0:
            click.echo("Terraform plan failed:")
            click.echo(plan_result.stderr)
            return

        click.echo(plan_result.stdout)

        # Apply Terraform configuration if user confirms
        if auto_apply or click.confirm("Would you like to apply the Terraform configuration now?"):
            click.echo("\nApplying Terraform configuration...\n")
            apply_result = subprocess.run(
                ["terraform", f"-chdir={infra_dir}", "apply", "-auto-approve"], capture_output=True, text=True
            )

            if apply_result.returncode != 0:
                click.echo("Terraform apply failed:")
                click.echo(apply_result.stderr)
                return

            click.echo(apply_result.stdout)

        # Prompt to apply the k8s configuration
        if not skip_apply and (
            auto_apply or click.confirm("Would you like to apply the Kubernetes configuration now?")
        ):
            # Get current kubectl context
            current_context_result = subprocess.run(
                ["kubectl", "config", "current-context"], capture_output=True, text=True
            )

            current_context = (
                current_context_result.stdout.strip() if current_context_result.returncode == 0 else "unknown"
            )
            # Get available contexts
            contexts_result = subprocess.run(
                ["kubectl", "config", "get-contexts", "-o", "name"], capture_output=True, text=True
            )

            if contexts_result.returncode != 0:
                click.echo("Failed to get kubectl contexts:")
                click.echo(contexts_result.stderr)
                return

            available_contexts = [context.strip() for context in contexts_result.stdout.splitlines() if context.strip()]

            if not available_contexts:
                click.echo("No kubectl contexts found. Configure kubectl first.")
                return

            # Prompt user to select a context
            if len(available_contexts) == 1:
                selected_context = available_contexts[0]
                click.echo(f"Using the only available kubectl context: {selected_context}")
            else:
                click.echo("\nAvailable kubectl contexts:")
                for i, context in enumerate(available_contexts):
                    marker = " (current)" if context == current_context else ""
                    click.echo(f"  {i + 1}. {context}{marker}")

                click.echo("")
                default_index = (
                    available_contexts.index(current_context) + 1 if current_context in available_contexts else 1
                )

                selected_index = click.prompt(
                    "Select kubectl context number to apply configuration",
                    type=click.IntRange(1, len(available_contexts)),
                    default=default_index,
                )

                selected_context = available_contexts[selected_index - 1]
                click.echo(f"Selected context: {selected_context}")

            # Apply the configuration to the selected context
            click.echo(f"Applying Kubernetes configuration to context '{selected_context}'...")
            apply_result = subprocess.run(
                ["kubectl", "--context", selected_context, "apply", "-f", str(yaml_path)],
                capture_output=True,
                text=True,
            )

            if apply_result.returncode != 0:
                click.echo("Failed to apply Kubernetes configuration:")
                click.echo(apply_result.stderr)
            else:
                click.echo("Kubernetes configuration applied successfully:")
                click.echo(apply_result.stdout)

                # Get the namespace from the applied configuration
                namespace = None
                with open(yaml_path, "r") as f:
                    for line in f:
                        if "namespace:" in line and not namespace:
                            namespace = line.split("namespace:")[1].strip()
                            break

                if not namespace:
                    namespace = "tinybird"  # Default namespace

                click.echo("\nWaiting for load balancer and DNS to be provisioned...")

                max_attempts = 30  # 30 attempts * 10 seconds = 5 minutes
                endpoint_url = f"https://{dns_record}.{dns_zone_name}"

                with click.progressbar(
                    range(max_attempts),
                    label=f"Checking endpoint availability: {endpoint_url}",
                    length=max_attempts,
                    show_eta=True,
                    show_percent=True,
                    fill_char="█",
                    empty_char="░",
                ) as bar:
                    for attempt in bar:
                        try:
                            response = requests.get(endpoint_url, allow_redirects=False, timeout=5)
                            if response.status_code < 400:  # Consider any non-error response as success
                                click.echo(click.style("\n✅ HTTPS endpoint is now accessible!", fg="green", bold=True))
                                break
                        except requests.RequestException:
                            pass

                        if attempt == max_attempts - 1:
                            click.echo(
                                click.style(
                                    "\n⚠️  HTTPS endpoint not accessible after 5 minutes", fg="yellow", bold=True
                                )
                            )
                            click.echo(
                                "  This might be due to DNS propagation or the Load Balancer provisioning delays"
                            )
                            click.echo(f"  Please try accessing {endpoint_url} manually in a few minutes")
                        else:
                            time.sleep(10)

    if not skip_apply:
        # Print a summary with the endpoint URL
        click.echo("\n" + "=" * 60)
        click.echo("DEPLOYMENT SUMMARY".center(60))
        click.echo("=" * 60)
        click.echo("✅ Load balancer provisioned")

        click.echo(f"\n🔗 Tinybird is available at: https://{dns_record}.{dns_zone_name}")

        click.echo(
            "\n📌 Note: It may take a few minutes for DNS to propagate and the HTTPS certificate to be fully provisioned."
        )


@infra.command(name="rm")
@click.argument("name")
@click.pass_context
@coro
async def infra_rm(ctx: click.Context, name: str):
    """Delete an infrastructure from Tinybird"""
    try:
        click.echo(FeedbackManager.highlight(message=f"\n» Deleting infrastructure '{name}' from Tinybird..."))
        client: TinyB = ctx.ensure_object(dict)["client"]
        user_workspaces = await client.user_workspaces_with_organization()
        admin_org_id = user_workspaces.get("organization_id")
        if not admin_org_id:
            raise CLIException("No organization associated to this workspace")
        infras = await client.infra_list(admin_org_id)
        infra_id = next((infra["id"] for infra in infras if infra["name"] == name), None)
        if not infra_id:
            raise CLIException(f"Infrastructure '{name}' not found")
        await client.infra_delete(infra_id, admin_org_id)
        click.echo(FeedbackManager.success(message=f"\n✓ Infrastructure '{name}' deleted"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"✗ Error: {e}"))


@infra.command(name="ls")
@click.pass_context
@coro
async def infra_ls(ctx: click.Context):
    """List self-managed infrastructures"""

    client: TinyB = ctx.ensure_object(dict)["client"]
    config = CLIConfig.get_project_config()
    user_client = config.get_client(token=config.get_user_token() or "")
    user_workspaces = await user_client.user_workspaces_with_organization()
    admin_org_id = user_workspaces.get("organization_id")
    infras = await client.infra_list(organization_id=admin_org_id)
    columns = [
        "name",
        "host",
    ]
    table_human_readable = []
    table_machine_readable = []

    for infra in infras:
        name = infra["name"]
        host = infra["host"]

        table_human_readable.append((name, host))
        table_machine_readable.append({"name": name, "host": host})

    click.echo(FeedbackManager.info(message="\n** Infras:"))
    echo_safe_humanfriendly_tables_format_smart_table(table_human_readable, column_names=columns)
    click.echo("\n")


@infra.command(name="create")
@click.option("--name", type=str, help="Name for identifying the self-managed infrastructure in Tinybird")
@click.option("--host", type=str, help="Host for the infrastructure")
@click.pass_context
@coro
async def infra_create(ctx: click.Context, name: str, host: str):
    """Create a self-managed infrastructure"""
    try:
        client: TinyB = ctx.ensure_object(dict)["client"]
        user_workspaces = await client.user_workspaces_with_organization()
        admin_org_id = user_workspaces.get("organization_id")
        if not admin_org_id:
            raise CLIException("No organization associated to this workspace")
        name = name or click.prompt("Enter name", type=str)
        host = host or click.prompt("Enter host", type=str)
        click.echo(FeedbackManager.highlight(message=f"\n» Creating infrastructure '{name}' in Tinybird..."))
        infra = await client.infra_create(organization_id=admin_org_id, name=name, host=host)
        click.echo(FeedbackManager.success(message=f"\n✓ Infrastructure '{name}' created"))
        pyperclip.copy(infra["token"])
        click.echo(FeedbackManager.info(message="Access token has been copied to your clipboard."))
        click.echo(
            FeedbackManager.info(message="Pass it as an environment variable in your deployment as TB_INFRA_TOKEN")
        )
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"✗ Error: {str(e)}"))


@infra.command(name="update")
@click.argument("infra_name")
@click.option("--name", type=str, help="Name for identifying the self-managed infrastructure in Tinybird")
@click.option("--host", type=str, help="Host for the infrastructure")
@click.pass_context
@coro
async def infra_update(ctx: click.Context, infra_name: str, name: str, host: str):
    """Update a self-managed infrastructure"""
    try:
        client: TinyB = ctx.ensure_object(dict)["client"]
        user_workspaces = await client.user_workspaces_with_organization()
        admin_org_id = user_workspaces.get("organization_id")
        if not admin_org_id:
            raise CLIException("No organization associated to this workspace")

        if not name and not host:
            click.echo(
                FeedbackManager.warning(message="No name or host provided. Please provide either a name or a host.")
            )
            return

        if name or host:
            infras = await client.infra_list(organization_id=admin_org_id)
            infra_id = next((infra["id"] for infra in infras if infra["name"] == infra_name), None)
            if not infra_id:
                raise CLIException(f"Infrastructure '{infra_name}' not found")
            click.echo(FeedbackManager.highlight(message=f"\n» Updating infrastructure '{infra_name}' in Tinybird..."))
            await client.infra_update(infra_id=infra_id, organization_id=admin_org_id, name=name, host=host)
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"✗ Error: {str(e)}"))
