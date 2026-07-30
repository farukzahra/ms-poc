#Requires -Version 5.1
<#
.SYNOPSIS
  Discover Azure AI resources for ms-poc and print env var candidates.
.DESCRIPTION
  Run after `az login`. Does not write secrets to disk except when -WriteEnv is passed to azure-fill-env.ps1.
#>
param(
    [string]$ResourceGroup = "rg-ai-sales-poc",
    [string]$SubscriptionId = ""
)

$ErrorActionPreference = "Stop"

function Invoke-Az {
    param([string[]]$Args)
    $out = & python -m azure.cli @Args 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($out -join "`n") }
    return $out
}

Write-Host "Checking Azure login..."
Invoke-Az @("account", "show", "-o", "none") | Out-Null

if ($SubscriptionId) {
    Invoke-Az @("account", "set", "--subscription", $SubscriptionId) | Out-Null
}

$sub = Invoke-Az @("account", "show", "-o", "json") | ConvertFrom-Json
Write-Host "Subscription: $($sub.name) ($($sub.id))"

Write-Host "`n--- Azure OpenAI / Cognitive Services (OpenAI kind) ---"
$openAiAccounts = Invoke-Az @(
    "cognitiveservices", "account", "list",
    "--query", "[?kind=='OpenAI'].{name:name,resourceGroup:resourceGroup,location:location,endpoint:properties.endpoint}",
    "-o", "json"
) | ConvertFrom-Json

if (-not $openAiAccounts) {
    Write-Host "No OpenAI accounts found in subscription."
} else {
    $openAiAccounts | Format-Table -AutoSize
    foreach ($acc in $openAiAccounts) {
        Write-Host "`nDeployments in $($acc.name):"
        Invoke-Az @(
            "cognitiveservices", "account", "deployment", "list",
            "-g", $acc.resourceGroup, "-n", $acc.name,
            "--query", "[].{name:name,model:properties.model.name,sku:sku.name}",
            "-o", "table"
        )
    }
}

Write-Host "`n--- Azure AI Search ---"
Invoke-Az @(
    "search", "service", "list",
    "--query", "[].{name:name,resourceGroup:resourceGroup,location:location,sku:sku.name}",
    "-o", "table"
)

Write-Host "`n--- Storage accounts (document candidates) ---"
Invoke-Az @(
    "storage", "account", "list",
    "--query", "[].{name:name,resourceGroup:resourceGroup,location:location,kind:kind}",
    "-o", "table"
)

Write-Host "`n--- Resource group '$ResourceGroup' ---"
$rg = Invoke-Az @("group", "exists", "-n", $ResourceGroup, "-o", "tsv")
if ($rg -eq "true") {
    Invoke-Az @("resource", "list", "-g", $ResourceGroup, "--query", "[].{name:name,type:type}", "-o", "table")
} else {
    Write-Host "Resource group does not exist yet."
}

Write-Host "`nNext: .\scripts\azure-fill-env.ps1 -OpenAiAccount <name> -ResourceGroup <rg> ..."
