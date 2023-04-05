# Receive-Job -Id 1 -Keep
# Get-job

## 생성과 동시에 호스트에 넣는 스크립트이다. ##
## Host관련 부분 주석, Zone 확인, Storage계정 확인, SPN 확인  ##

# $tenantId = ""
# $securePassword = ConvertTo-SecureString "" -AsPlainText -Force
# $credential = New-Object System.Management.Automation.PSCredential("",$securePassword)
# Login-AzAccount -Credential $credential -ServicePrincipal -TenantId $tenantId | Out-Null
# Set-AzContext -Subscription "" | Out-Null

# AzureCLI
# $subscriptionId = ""
# az login
# az account set --subscription $subscriptionId

Function Create-VMs { 
    Param(
        [Parameter(Mandatory=$True,HelpMessage='Enter the Path to your CSV')]  
        [string]$csvpath # 
    )
    $testpath = Test-Path -Path $csvpath
    If (!$testpath){
        clear-host
        write-host -ForegroundColor Red '***** Invalid CSV Path *****' -ErrorAction Stop
    } else {
        
        Import-Csv -Path "$csvPath" | ForEach-Object {

            Start-Job -ScriptBlock {
                Param($ResourceGroupName, $Location, $VMName, $VNetName, $VNetRGName, $SubnetName, $PipFlag, $PrivateIPAddress, $VMSize, $SADiagName, $SAResourceGroup, $LoginProfilePath, `
                    $AVSetName, $OSType, $PublisherName, $Offer, $Skus, $Version, $OSDiskType, $OsDiskSize, $NSGName, $NSGRgName, $DataDiskSize, $DataDiskType, $DiskName, $Zone, $HostGroupName, $HostRgName, $HostName) 

                    $AdminUsername = '' #VM 계정
                    $AdminPassword = '' #VM 암호
                    $PipName = "PIP-" + $VMName
                    $NicName = "NIC-" + $VMName
                    $OsDiskName = "OSDISK-" + $VMName
                    $DataDiskName = "DATADISK-" + $VMName
                    $Zone = [int]$Zone

                    # Post Script Variable
                    $storageAccountName = ""
                    $storageAccountKey = ""
                    $ProtectedSettings = @{"storageAccountName" = $storageAccountName; "storageAccountKey" = $storageAccountKey}
                    $winuri = ""
                    $winSettings = @{"fileUris" = @($winuri); "commandToExecute" = "powershell -ExecutionPolicy Unrestricted -File 123.ps1"}   

                    # Create User Object (VM)
                    $cred = New-Object PSCredential $AdminUsername, ($AdminPassword | ConvertTo-SecureString -AsPlainText -Force)

                    # Create a NIC
                    $vnet = Get-AzVirtualNetwork -Name $vnetName -ResourceGroupName $vnetRGName 
                    $subnet = Get-AzVirtualNetworkSubnetConfig -VirtualNetwork $vnet -Name $subnetName
                    $NSG = Get-AzNetworkSecurityGroup -Name $NSGName -ResourceGroupName $NSGRgName                  
                    if($PipFlag -eq 'Y') { 
                        # Create a public IP address and specify a DNS name (DomainNameLabel)
                        $pip = New-AzPublicIpAddress -ResourceGroupName $ResourceGroupName -Location $Location -Name $pipName -AllocationMethod Static -Sku Standard #-Zone $Zone

                        # Create a NIC(with PIP)                        
                        $nic = New-AzNetworkInterface -Name $nicName -ResourceGroupName $resourceGroupName -Subnet $subnet -Location $location -PrivateIpAddress $privateIPAddress `
                            -PublicIpAddress $pip -EnableAcceleratedNetworking -NetworkSecurityGroup $NSG
                    } else {    
                        # Create a NIC
                        $nic = New-AzNetworkInterface -Name $nicName -ResourceGroupName $resourceGroupName -Subnet $subnet -Location $location -PrivateIpAddress $privateIPAddress `
                        -EnableAcceleratedNetworking -NetworkSecurityGroup $NSG                                      
                    }

                    # Create VM   ---> AVSet 적용 시키는 VM인지 아닌지에 따라 주석 수정
                    #  $AVSetID = Get-AzAvailabilitySet -ResourceGroupName $resourceGroupName -Name $AVSetName
                     $VirtualMachine = New-AzVMConfig -VMName $VMName -VMSize $VMSize #-Zone $Zone #-AvailabilitySetID $AVSetID.Id

                    if ($OSType -eq 'Windows') { #OSTyep이 Windows일 경우
                        $VirtualMachine = Set-AzVMOperatingSystem -VM $VirtualMachine -Windows -ComputerName $VMName -Credential $Cred -ProvisionVMAgent -TimeZone "Korea Standard Time" -EnableAutoUpdate:$false
                        
                        $VirtualMachine = Set-AzVMSourceImage -VM $VirtualMachine -PublisherName $PublisherName -Offer $Offer -Skus $Skus -Version $Version 
                        $VirtualMachine = Set-AzVMOSDisk -VM $VirtualMachine -Name $OsDiskName -StorageAccountType $OSDiskType -DiskSizeInGB $OsDiskSize -CreateOption FromImage -Caching ReadWrite                                     

                        $VirtualMachine = Add-AzVMNetworkInterface -VM $VirtualMachine -Id $nic.Id

                        # Attach to dedicated hostgroup(host)
                        if($HostName -ne $null){
                            $myDH = Get-AzHost -HostGroupName $HostGroupName -ResourceGroupName $HostRgName -Name $HostName
                            $VirtualMachine.Host = New-Object Microsoft.Azure.Management.Compute.Models.SubResource
                            $VirtualMachine.Host.Id = $myDH.Id
                        }

                        if($DataDiskSize -ne 'N'){ 
                            $DataDiskConfig = New-AzDiskConfig -Location $Location -SkuName $DataDiskType -CreateOption Empty -DiskSizeGB $DataDiskSize #-Zone $Zone                       
                            $DataDisk = New-AzDisk -DiskName $DataDiskName -ResourceGroupName $ResourceGroupName -Disk $DataDiskConfig
                            $VirtualMachine = Add-AzVMDataDisk -VM $VirtualMachine -Name $DataDiskName -Lun 0 -CreateOption Attach -ManagedDiskId $DataDisk.Id
                        }                                                

                        $VirtualMachine = Set-AzVMBootDiagnostic -VM $VirtualMachine -Enable -ResourceGroupName $SAResourceGroup -StorageAccountName $SADiagName
                        
                        New-AzVM -ResourceGroupName $ResourceGroupName -Location $Location -VM $VirtualMachine -Verbose #-LicenseType "Windows_Server"                                                                                   

                        Set-AzVMExtension -ResourceGroupName $ResourceGroupName -Location $Location -VMName $VMName -Name CSE `
                        -Publisher "Microsoft.Compute" -Type "CustomScriptExtension" -TypeHandlerVersion 1.9 -Settings $winSettings -ProtectedSettings $ProtectedSettings
                    
                        
                    } else {  
                        $VirtualMachine = Set-AzVMOperatingSystem -VM $VirtualMachine -Linux -ComputerName $VMName -Credential $Cred
                        $VirtualMachine = Set-AzVMSourceImage -VM $VirtualMachine -PublisherName $PublisherName -Offer $Offer -Skus $Skus -Version $Version                                                
                        $VirtualMachine = Set-AzVMOSDisk -VM $VirtualMachine -Name $OsDiskName -StorageAccountType $OSDiskType -DiskSizeInGB $OsDiskSize -CreateOption FromImage -Caching ReadWrite                      
                        
                        $VirtualMachine = Add-AzVMNetworkInterface -VM $VirtualMachine -Id $nic.Id     
                        
                        # Attach to dedicated hostgroup(host)
                        if($HostName -ne $null){
                        $myDH = Get-AzHost -HostGroupName $HostGroupName -ResourceGroupName $HostRgName -Name $HostName
                        $VirtualMachine.Host = New-Object Microsoft.Azure.Management.Compute.Models.SubResource
                        $VirtualMachine.Host.Id = $myDH.Id
                        }

                        if($DataDiskSize -ne 'N'){ 
                            $DataDiskConfig = New-AzDiskConfig -SkuName $DataDiskType -Location $Location -DiskSizeGB $DataDiskSize -CreateOption Empty #-Zone $Zone
                            $DataDisk = New-AzDisk -DiskName $DataDiskName -ResourceGroupName $ResourceGroupName -Disk $DataDiskConfig
                            $VirtualMachine = Add-AzVMDataDisk -VM $VirtualMachine -Name $DataDiskName -Lun 0 -CreateOption Attach -ManagedDiskId $DataDisk.Id
                        }
                        $VirtualMachine = Set-AzVMBootDiagnostic -VM $VirtualMachine -Enable -ResourceGroupName $SAResourceGroup -StorageAccountName $SADiagName #부트진단 설정
                        New-AzVM -ResourceGroupName $ResourceGroupName -Location $Location -VM $VirtualMachine -Verbose    
                                       
                    }               
            } -ArgumentList $_.ResourceGroupName, $_.Location, $_.VMName, $_.VNetName, $_.VNetRGName, $_.SubnetName, $_.PipFlag, $_.PrivateIPAddress, $_.VMSize, $_.SADiagName, $_.SAResourceGroup, $_.LoginProfilePath, `
            $_.AVSetName, $_.OSType, $_.PublisherName, $_.Offer, $_.Skus, $_.Version, $_.OSDiskType, $_.OsDiskSize, $_.NSGName, $_.NSGRgName, $_.DataDiskSize, $_.DataDiskType, $_.DiskName,$_.Zone, $_.HostGroupName, $_.HostRgName, $_.HostName
        }
    }
}