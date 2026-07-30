param location string
param environmentName string

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: replace('${environmentName}acr', '-', '')
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
  }
}

output loginServer string = acr.properties.loginServer
output registryName string = acr.name
