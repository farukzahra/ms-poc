targetScope = 'subscription'

@description('Enterprise AI Sales Intelligence POC infrastructure')
param location string = 'eastus'
param environmentName string = 'ms-poc-dev'
param tenantId string = subscription().tenantId
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    location: location
    environmentName: environmentName
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    location: location
    environmentName: environmentName
  }
}

module search 'modules/search.bicep' = {
  name: 'search'
  params: {
    location: location
    environmentName: environmentName
  }
}

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault'
  params: {
    location: location
    environmentName: environmentName
    tenantId: tenantId
  }
}

module acr 'modules/acr.bicep' = {
  name: 'acr'
  params: {
    location: location
    environmentName: environmentName
  }
}

module containerApps 'modules/container-apps.bicep' = {
  name: 'container-apps'
  params: {
    location: location
    environmentName: environmentName
    appInsightsConnectionString: monitoring.outputs.connectionString
    containerImage: containerImage
  }
}

output containerAppFqdn string = containerApps.outputs.apiFqdn
output appInsightsConnectionString string = monitoring.outputs.connectionString
output storageAccountName string = storage.outputs.storageAccountName
output searchEndpoint string = search.outputs.searchEndpoint
output keyVaultUri string = keyVault.outputs.keyVaultUri
output acrLoginServer string = acr.outputs.loginServer
