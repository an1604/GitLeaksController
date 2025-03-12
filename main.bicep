@description('The name of the storage account')
param storageAccountName string = 'storage${uniqueString(resourceGroup().id)}'

@description('The location for all resources')
param location string = resourceGroup().location

@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_ZRS'
  'Premium_LRS'
])
param storageAccountSku string = 'Standard_LRS'

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageAccountSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

module appService './modules/appService.bicep' = {
  name: 'appServiceDeploy'
  params: {
    location: location
    appServiceName: 'app-${uniqueString(resourceGroup().id)}'
  }
}

output storageAccountId string = storageAccount.id
output appServiceUrl string = appService.outputs.appServiceUrl 