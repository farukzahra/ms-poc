targetScope = 'subscription'

@description('Enterprise AI Sales Intelligence POC infrastructure')
param location string = 'eastus'
param environmentName string = 'ms-poc-dev'

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
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
  }
}

output containerAppFqdn string = containerApps.outputs.apiFqdn
output appInsightsConnectionString string = monitoring.outputs.connectionString
