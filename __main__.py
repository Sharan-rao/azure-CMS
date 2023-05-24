import pulumi
from pulumi_azure_native import resources, storage, keyvault

tenantId = "52c5f229-1e7a-4773-af5a-ef52db324ced"
objectId = "d46510dc-7a3c-4275-b1c0-edc843a90a5f"

# Create an Azure Resource Group
resource_group = resources.ResourceGroup("resourceGroup")

# Create an Azure Key Vault
key_vault = keyvault.Vault("vault", 
    properties=keyvault.VaultPropertiesArgs(
        access_policies=[keyvault.AccessPolicyEntryArgs(
            object_id=objectId,
            permissions=keyvault.PermissionsArgs(
                certificates=[
                    "get",
                    "list",
                    "delete",
                    "create",
                    "import",
                    "update",
                    "managecontacts",
                    "getissuers",
                    "listissuers",
                    "setissuers",
                    "deleteissuers",
                    "manageissuers",
                    "recover",
                    "purge",
                ],
                keys=[
                    "encrypt",
                    "decrypt",
                    "wrapKey",
                    "unwrapKey",
                    "sign",
                    "verify",
                    "get",
                    "list",
                    "create",
                    "update",
                    "import",
                    "delete",
                    "backup",
                    "restore",
                    "recover",
                    "purge",
                ],
                secrets=[
                    "get",
                    "list",
                    "set",
                    "delete",
                    "backup",
                    "restore",
                    "recover",
                    "purge",
                ],
            ),
            tenant_id=tenantId,
        )],
        enabled_for_deployment=True,
        enabled_for_disk_encryption=True,
        enabled_for_template_deployment=True,
        sku=keyvault.SkuArgs(
            family="A",
            name="standard",
        ),
    tenant_id=tenantId,
    ),
    resource_group_name=resource_group.name,
    vault_name="kyvault45") #change the vault name

# Create a Key in the Key Vault
key = keyvault.Key("key",
    resource_group_name=resource_group.name,
    vault_name=key_vault.name,
    properties={
        "kty": "RSA",
        "key_ops": ["encrypt", "decrypt"],
    })

# Create a storage account with encryption at rest enabled
storage_account = storage.StorageAccount("stg",
    resource_group_name=resource_group.name,
    #account_replication_type="LRS",
    sku={
        "name": "Standard_LRS",
    },
    kind="StorageV2",
    location=resource_group.location,
    enable_https_traffic_only=True,
    encryption={
        "services": {
            "blob": {"enabled": True},
            "file": {"enabled": True}
        },
        "key_source": "Microsoft.Keyvault",
        "key_vault_properties": {
            "key_name": key.name,
            "key_vault_uri": key_vault.properties.vault_uri
        }
    },
)

# Get the Storage Account Keys
storage_account_keys = pulumi.Output.all(resource_group.name, storage_account.name).apply(
    lambda args: storage.list_storage_account_keys(resource_group_name=args[0], account_name=args[1]))

# Get the Primary Connection String
primary_key = storage_account_keys.apply(lambda keys: keys.keys[0].value)
connection_string = pulumi.Output.all(storage_account.name, primary_key).apply(
    lambda args: f"DefaultEndpointsProtocol=https;AccountName={args[0]};AccountKey={args[1]};EndpointSuffix=core.windows.net")

# Export the storage account connection string
pulumi.export("storage_account_connection_string", connection_string)
pulumi.export("storage_account_name", storage_account.name)