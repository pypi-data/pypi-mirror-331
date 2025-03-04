import json
import uuid
from pathlib import Path
from typing import Optional

import click
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
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: 'external'
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: 'ip'
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: 'tcp'
    service.beta.kubernetes.io/aws-load-balancer-scheme: 'internet-facing'
    service.beta.kubernetes.io/aws-load-balancer-ssl-negotiation-policy: 'ELBSecurityPolicy-TLS13-1-2-2021-06'
    service.beta.kubernetes.io/aws-load-balancer-ssl-cert: '%(cert_arn)s'
spec:
  type: LoadBalancer
  ports:
    - port: 443
      targetPort: http
      protocol: TCP
      name: https
  selector:
    name: tinybird
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: tinybird
  namespace:  %(namespace)s
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
  name = "%(domain)s"
}

# Create ACM certificate
resource "aws_acm_certificate" "cert" {
  domain_name               = "*.${data.aws_route53_zone.selected.name}"
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

output "certificate_arn" {
  description = "The ARN of the ACM certificate"
  value       = aws_acm_certificate.cert.arn
}
"""

TERRAFORM_SECOND_TEMPLATE = """
# Create Route 53 record for the load balancer
resource "aws_route53_record" "tinybird" {
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = "%(full_dns_name)s"
  type    = "CNAME"
  ttl     = 300
  records = ["%(external_ip)s"]
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
@click.option("--provider", default="aws", type=str, help="Infrastructure provider (aws, gcp, azure)")
@click.option("--region", type=str, help="AWS region (for AWS provider)")
@click.option("--domain", type=str, help="Route53 domain name (for AWS provider)")
@click.option("--namespace", type=str, help="Kubernetes namespace for deployment")
@click.option("--dns-record", type=str, help="DNS record name to create (without domain, e.g. 'tinybird')")
@click.option(
    "--auto-apply-terraform", is_flag=True, help="Automatically apply Terraform configuration without prompting"
)
@click.option("--auto-apply-dns", is_flag=True, help="Automatically apply DNS configuration without prompting")
@click.option(
    "--auto-apply-kubectl", is_flag=True, help="Automatically apply Kubernetes configuration without prompting"
)
@click.option("--skip-terraform", is_flag=True, help="Skip Terraform configuration and application")
@click.option("--skip-kubectl", is_flag=True, help="Skip Kubernetes configuration and application")
@click.option("--skip-dns", is_flag=True, help="Skip DNS configuration and application")
@click.pass_context
def infra_init(
    ctx: Context,
    name: str,
    provider: str,
    region: Optional[str] = None,
    domain: Optional[str] = None,
    namespace: Optional[str] = None,
    dns_record: Optional[str] = None,
    storage_class: Optional[str] = None,
    auto_apply_terraform: bool = False,
    auto_apply_dns: bool = False,
    auto_apply_kubectl: bool = False,
    skip_terraform: bool = False,
    skip_kubectl: bool = False,
    skip_dns: bool = False,
) -> None:
    """Init infra"""
    # AWS-specific Terraform template creation
    if provider.lower() != "aws":
        click.echo("Provider not supported yet.")
        return

    # Create infra directory if it doesn't exist
    infra_dir = Path("infra")
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
            click.echo("Warning: Could not parse existing config.json, will create a new one")

    # Generate a random ID for default values
    random_id = str(uuid.uuid4())[:8]

    # Get or prompt for configuration values
    name = name or click.prompt("Enter name", type=str)
    region = region or config.get("region") or click.prompt("Enter aws region", default="us-east-1", type=str)
    domain = domain or config.get("domain") or click.prompt("Enter route 53 domain name", type=str)
    namespace = (
        namespace
        or config.get("namespace")
        or click.prompt("Enter namespace name", default=f"tinybird-{random_id}", type=str)
    )
    dns_record = (
        dns_record
        or config.get("dns_record")
        or click.prompt("Enter DNS record name (without domain)", default=f"tinybird-{random_id}", type=str)
    )
    storage_class = config.get("storage_class") or click.prompt(
        "Enter storage class", default="gp3-encrypted", type=str
    )

    # Save configuration
    config = {
        "provider": provider,
        "region": region,
        "domain": domain,
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
    infras = async_to_sync(client.infra_list)(organization_id=admin_org_id)
    infra = next((infra for infra in infras if infra["name"] == name), None)
    if not infra:
        click.echo(FeedbackManager.highlight(message=f"\n» Creating infrastructure '{name}' in Tinybird..."))
        host = f"https://{dns_record}.{domain}"
        infra = async_to_sync(client.infra_create)(organization_id=admin_org_id, name=name, host=host)

    infra_token = infra["token"]

    # Write the Terraform template
    terraform_content = TERRAFORM_FIRST_TEMPLATE % {"aws_region": region, "domain": domain}

    with open(tf_path, "w") as f:
        f.write(terraform_content.lstrip())

    click.echo(f"Creating Terraform configuration in {tf_path}")

    # Apply Terraform configuration if user confirms
    if not skip_terraform:
        import subprocess

        # Initialize Terraform
        click.echo("Initializing Terraform...")
        init_result = subprocess.run(["terraform", "-chdir=infra", "init"], capture_output=True, text=True)

        if init_result.returncode != 0:
            click.echo("Terraform initialization failed:")
            click.echo(init_result.stderr)
            return

        # Run terraform plan first
        click.echo("\nRunning Terraform plan...\n")
        plan_result = subprocess.run(["terraform", "-chdir=infra", "plan"], capture_output=True, text=True)

        if plan_result.returncode != 0:
            click.echo("Terraform plan failed:")
            click.echo(plan_result.stderr)
            return

        click.echo(plan_result.stdout)

        # Apply Terraform configuration if user confirms
        if auto_apply_terraform or click.confirm("Would you like to apply the Terraform configuration now?"):
            click.echo("\nApplying Terraform configuration...\n")
            apply_result = subprocess.run(
                ["terraform", "-chdir=infra", "apply", "-auto-approve"], capture_output=True, text=True
            )

            if apply_result.returncode != 0:
                click.echo("Terraform apply failed:")
                click.echo(apply_result.stderr)
                return

            click.echo(apply_result.stdout)

            # Get the certificate ARN output
            output_result = subprocess.run(
                ["terraform", "-chdir=infra", "output", "certificate_arn"], capture_output=True, text=True
            )

            if output_result.returncode == 0:
                cert_arn = output_result.stdout.strip().replace('"', "")

                new_content = K8S_YML % {
                    "namespace": namespace,
                    "cert_arn": cert_arn,
                    "storage_class": storage_class,
                    "infra_token": infra_token,
                }

                with open(yaml_path, "w") as f:
                    f.write(new_content.lstrip())

                click.echo(f"Created Kubernetes configuration with certificate ARN in {yaml_path}")

                # Prompt to apply the k8s configuration
                if not skip_kubectl and (
                    auto_apply_kubectl or click.confirm("Would you like to apply the Kubernetes configuration now?")
                ):
                    import subprocess

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

                    available_contexts = [
                        context.strip() for context in contexts_result.stdout.splitlines() if context.strip()
                    ]

                    if not available_contexts:
                        click.echo("No kubectl contexts found. Please configure kubectl first.")
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
                            available_contexts.index(current_context) + 1
                            if current_context in available_contexts
                            else 1
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

                        click.echo(f"\nWaiting for load balancer to be provisioned in namespace '{namespace}'...")

                        # Wait for the load balancer to get an external IP
                        max_attempts = 30
                        attempt = 0
                        external_ip = None

                        while attempt < max_attempts and not external_ip:
                            attempt += 1

                            # Get the service details
                            get_service_result = subprocess.run(
                                [
                                    "kubectl",
                                    "--context",
                                    selected_context,
                                    "-n",
                                    namespace,
                                    "get",
                                    "service",
                                    "tinybird",
                                    "-o",
                                    "jsonpath='{.status.loadBalancer.ingress[0].hostname}'",
                                ],
                                capture_output=True,
                                text=True,
                            )

                            if get_service_result.returncode == 0:
                                potential_ip = get_service_result.stdout.strip().replace("'", "")
                                if potential_ip and potential_ip != "":
                                    external_ip = potential_ip
                                    break

                            click.echo(
                                f"Attempt {attempt}/{max_attempts}: Load balancer not ready yet, waiting 10 seconds..."
                            )
                            import time

                            time.sleep(10)

                        if external_ip:
                            click.echo("\nLoad balancer provisioned successfully.")

                            # Update the Terraform configuration with the load balancer DNS
                            if not skip_dns and domain and tf_path.exists():
                                click.echo("\nUpdating Terraform configuration with load balancer DNS...")

                                with open(tf_path, "r") as f:
                                    tf_content = f.read()

                                # Check if the Route 53 record already exists in the file
                                if 'resource "aws_route53_record" "tinybird"' not in tf_content:
                                    # Create the full DNS name
                                    full_dns_name = f"{dns_record}.{domain}"

                                    # Use in the Terraform template
                                    route53_record = TERRAFORM_SECOND_TEMPLATE % {
                                        "external_ip": external_ip,
                                        "full_dns_name": full_dns_name,
                                    }

                                    # Append the Route 53 record to the Terraform file
                                    with open(tf_path, "a") as f:
                                        f.write(route53_record.lstrip())

                                    click.echo("Added Route 53 record to Terraform configuration")
                                else:
                                    # Update the existing Route 53 record
                                    updated_tf = tf_content.replace(
                                        'records = ["LOAD_BALANCER_DNS_PLACEHOLDER"]', f'records = ["{external_ip}"]'
                                    )

                                    # Also handle case where there might be another placeholder or old value
                                    import re

                                    pattern = r'records\s*=\s*\[\s*"[^"]*"\s*\]'
                                    updated_tf = re.sub(pattern, f'records = ["{external_ip}"]', updated_tf)

                                    with open(tf_path, "w") as f:
                                        f.write(updated_tf.lstrip())

                                    click.echo("Updated existing Route 53 record in Terraform configuration")

                                # Run terraform plan for DNS changes
                                click.echo("\nRunning Terraform plan for DNS changes...\n")
                                plan_result = subprocess.run(
                                    ["terraform", "-chdir=infra", "plan"], capture_output=True, text=True
                                )

                                if plan_result.returncode != 0:
                                    click.echo("Terraform plan for DNS changes failed:")
                                    click.echo(plan_result.stderr)
                                else:
                                    click.echo(plan_result.stdout)

                                    # Apply the updated Terraform configuration
                                    if not skip_dns and (
                                        auto_apply_dns
                                        or click.confirm("Would you like to create the DNS record in Route 53 now?")
                                    ):
                                        click.echo("Applying updated Terraform configuration...")
                                        apply_result = subprocess.run(
                                            ["terraform", "-chdir=infra", "apply", "-auto-approve"],
                                            capture_output=True,
                                            text=True,
                                        )

                                        if apply_result.returncode != 0:
                                            click.echo("Failed to create DNS record:")
                                            click.echo(apply_result.stderr)
                                        else:
                                            click.echo(apply_result.stdout)
                                            click.echo("DNS record created successfully!")

                                            # Get the DNS name from Terraform output
                                            dns_output = subprocess.run(
                                                ["terraform", "-chdir=infra", "output", "tinybird_dns"],
                                                capture_output=True,
                                                text=True,
                                            )

                                            if dns_output.returncode == 0:
                                                dns_name = dns_output.stdout.strip().replace('"', "")
                                                click.echo("\nDNS record created successfully!")
                                                click.echo(
                                                    "\nWaiting up to 5 minutes for HTTPS endpoint to become available..."
                                                )

                                                import time

                                                import requests

                                                max_attempts = 30  # 30 attempts * 10 seconds = 5 minutes
                                                attempt = 0
                                                while attempt < max_attempts:
                                                    attempt += 1
                                                    try:
                                                        response = requests.get(
                                                            f"https://{dns_name}", allow_redirects=False, timeout=5
                                                        )
                                                        response.raise_for_status()
                                                        click.echo("\n✅ HTTPS endpoint is now accessible!")
                                                        break
                                                    except requests.RequestException:
                                                        if attempt == max_attempts:
                                                            click.echo(
                                                                "\n⚠️  HTTPS endpoint not accessible after 5 minutes"
                                                            )
                                                            click.echo(
                                                                "  This might be due to DNS propagation or the Load Balancer provisioning delays"
                                                            )
                                                            click.echo(
                                                                "  Please try accessing the URL manually in a few minutes"
                                                            )
                                                        else:
                                                            click.echo(
                                                                f"Attempt {attempt}/{max_attempts}: Not ready yet, waiting 10 seconds..."
                                                            )
                                                            time.sleep(10)
                                            else:
                                                click.echo(
                                                    f"\nYour Tinybird instance should be available at: https://tinybird.{domain}"
                                                )

    # Print a summary with the endpoint URL
    click.echo("\n" + "=" * 60)
    click.echo("DEPLOYMENT SUMMARY".center(60))
    click.echo("=" * 60)

    if not skip_kubectl and external_ip:
        click.echo(f"✅ Load balancer provisioned: {external_ip}")

    if not skip_dns and not skip_terraform and domain:
        # Try to get the DNS name from Terraform output
        dns_output = subprocess.run(
            ["terraform", "-chdir=infra", "output", "tinybird_dns"], capture_output=True, text=True
        )

        if dns_output.returncode == 0:
            dns_name = dns_output.stdout.strip().replace('"', "")
            click.echo(f"✅ DNS record created: {dns_name}")
            click.echo(f"\n🔗 Tinybird is available at: https://{dns_name}")
        else:
            # Fallback to constructed DNS name
            full_dns_name = f"{dns_record}.{domain}"
            click.echo(f"✅ DNS record created: {full_dns_name}")
            click.echo(f"\n🔗 Tinybird is available at: https://{full_dns_name}")
    elif not skip_kubectl and external_ip:
        click.echo(f"\n🔗 Tinybird is available at: https://{external_ip}")
        if domain:
            click.echo(f"\n📝 Consider creating a DNS record: {dns_record}.{domain} → {external_ip}")

    click.echo(
        "\n📌 Note: It may take a few minutes for DNS to propagate and the HTTPS certificate to be fully provisioned."
    )
    click.echo("=" * 60)


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
