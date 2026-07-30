#Requires -Version 5.1
<#
.SYNOPSIS
  Fill ms-poc .env with Azure connection settings (gitignored).
.PARAMETER OpenAiAccount
  Cognitive Services account name (kind OpenAI).
.PARAMETER ChatDeployment
  Chat model deployment name (e.g. gpt-4o-mini).
.PARAMETER EmbeddingDeployment
  Embedding deployment name (e.g. text-embedding-3-small).
.PARAMETER SearchService
  Azure AI Search service name.
.PARAMETER StorageAccount
  Storage account name for documents container.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$OpenAiAccount,
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,
    [string]$ChatDeployment = "gpt-4o-mini",
    [string]$EmbeddingDeployment = "text-embedding-3-small",
    [string]$SearchService = "",
    [string]$SearchIndex = "enterprise-knowledge",
    [string]$StorageAccount = "",
    [string]$EnvPath = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $EnvPath) { $EnvPath = Join-Path $root ".env" }

function Invoke-AzJson {
    param([string[]]$Args)
    $raw = & python -m azure.cli @Args 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($raw -join "`n") }
    return ($raw | Out-String) | ConvertFrom-Json
}

Write-Host "Fetching OpenAI endpoint and key..."
$account = Invoke-AzJson @(
    "cognitiveservices", "account", "show",
    "-g", $ResourceGroup, "-n", $OpenAiAccount,
    "-o", "json"
)
$keys = Invoke-AzJson @(
    "cognitiveservices", "account", "keys", "list",
    "-g", $ResourceGroup, "-n", $OpenAiAccount,
    "-o", "json"
)

$endpoint = $account.properties.endpoint
$apiKey = $keys.key1

$lines = @{}
if (Test-Path $EnvPath) {
    Get-Content $EnvPath | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            $lines[$matches[1].Trim()] = $matches[2].Trim()
        }
    }
}

$lines["AZURE_AI_ENDPOINT"] = $endpoint
$lines["AZURE_AI_API_KEY"] = $apiKey
$lines["AZURE_CHAT_DEPLOYMENT"] = $ChatDeployment
$lines["AZURE_EMBEDDING_DEPLOYMENT"] = $EmbeddingDeployment

if ($SearchService) {
    Write-Host "Fetching Search endpoint and key..."
    $search = Invoke-AzJson @("search", "service", "show", "-g", $ResourceGroup, "-n", $SearchService, "-o", "json")
    $searchKeys = Invoke-AzJson @("search", "admin-key", "show", "--service-name", $SearchService, "-g", $ResourceGroup, "-o", "json")
    $lines["AZURE_SEARCH_ENDPOINT"] = "https://$SearchService.search.windows.net"
    $lines["AZURE_SEARCH_INDEX"] = $SearchIndex
    $lines["AZURE_SEARCH_API_KEY"] = $searchKeys.primaryKey
}

if ($StorageAccount) {
    Write-Host "Fetching Storage connection string..."
    $conn = & python -m azure.cli storage account show-connection-string -g $ResourceGroup -n $StorageAccount --query connectionString -o tsv 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($conn -join "`n") }
    $lines["AZURE_STORAGE_ACCOUNT"] = $StorageAccount
    $lines["AZURE_STORAGE_CONNECTION_STRING"] = $conn.Trim()
}

$order = @(
    "AZURE_AI_ENDPOINT", "AZURE_AI_API_KEY", "AZURE_CHAT_DEPLOYMENT", "AZURE_EMBEDDING_DEPLOYMENT",
    "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_INDEX", "AZURE_SEARCH_API_KEY",
    "AZURE_STORAGE_ACCOUNT", "AZURE_STORAGE_CONNECTION_STRING",
    "APPLICATIONINSIGHTS_CONNECTION_STRING",
    "AZURE_AD_TENANT_ID", "AZURE_AD_CLIENT_ID", "AZURE_AD_CLIENT_SECRET",
    "MCP_SERVER_URL", "CRM_API_URL", "SALES_API_URL", "TICKETS_API_URL", "CONTRACTS_API_URL", "PRODUCTS_API_URL",
    "CHUNK_SIZE", "CHUNK_OVERLAP", "API_HOST", "API_PORT", "CORS_ORIGIN", "DEV_AUTH_ENABLED"
)

$defaults = @{
    MCP_SERVER_URL = "http://localhost:8001"
    CRM_API_URL = "http://localhost:8101"
    SALES_API_URL = "http://localhost:8102"
    TICKETS_API_URL = "http://localhost:8103"
    CONTRACTS_API_URL = "http://localhost:8104"
    PRODUCTS_API_URL = "http://localhost:8105"
    CHUNK_SIZE = "800"
    CHUNK_OVERLAP = "120"
    API_HOST = "0.0.0.0"
    API_PORT = "8000"
    CORS_ORIGIN = "http://localhost:5200"
    DEV_AUTH_ENABLED = "true"
}

foreach ($key in $defaults.Keys) {
    if (-not $lines.ContainsKey($key)) { $lines[$key] = $defaults[$key] }
}

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("# Generated/updated by scripts/azure-fill-env.ps1 - DO NOT COMMIT")
foreach ($key in $order) {
    if ($lines.ContainsKey($key)) {
        [void]$sb.AppendLine("$key=$($lines[$key])")
    }
}
foreach ($key in ($lines.Keys | Sort-Object)) {
    if ($key -notin $order) {
        [void]$sb.AppendLine("$key=$($lines[$key])")
    }
}

Set-Content -Path $EnvPath -Value $sb.ToString().TrimEnd() -Encoding UTF8
Write-Host "Updated $EnvPath (secrets not printed)."
Write-Host "Restart API: docker compose up -d --force-recreate api"
