
## Use Cases for Network Models

The table below provides an overview of three different network models available in Azure Kubernetes Service (AKS): Kubenet, Azure CNI, and Azure CNI Overlay. Each network model has its unique set of use cases and advantages, depending on the specific requirements and constraints of the Kubernetes cluster.

| Network Model    | When to use                                                                                                        |
| ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| Kubenet          | - IP address space conservation is a priority<br>- Simple configuration<br>- Fewer than 400 nodes per cluster<br>- Kubernetes internal or external load balancers sufficient for reaching pods from outside the cluster<br>- Manually managing and maintaining user-defined routes is acceptable |
| Azure CNI        | - Full virtual network connectivity is required for pods<br>- Advanced AKS features (such as virtual nodes) are needed<br>- Sufficient IP address space is available<br>- Pod to pod and pod to VM connectivity needed<br>- External resources need to reach pods directly<br>- AKS network policies are required |
| Azure CNI Overlay | - IP address shortage is a concern<br>- Scaling up to 1000 nodes and 250 pods per node is sufficient<br>- Additional hop for pod connectivity is acceptable<br>- Complex network configuration is not a barrier<br>- AKS egress requirements can be met |

##Comparison of Network Models

The following table compares the capabilities and characteristics of three network models in Azure Kubernetes Service (AKS): Kubenet, Azure CNI, and Azure CNI Overlay. Understanding the differences between these models is crucial for selecting the appropriate network model based on the specific requirements of your Kubernetes cluster.


| Capability                                                                 | Kubenet                    | Azure CNI                  | Azure CNI Overlay         |
| -------------------------------------------------------------------------- | -------------------------- | -------------------------- | ------------------------- |
| Deploy cluster in existing or new virtual network                          | Supported - UDRs manually applied | Supported                  | Supported                 |
| Pod-pod connectivity                                                       | Supported                  | Supported                  | Supported                 |
| Pod-VM connectivity; VM in the same virtual network                        | Works when initiated by pod | Works both ways            | Works both ways           |
| Pod-VM connectivity; VM in peered virtual network                          | Works when initiated by pod | Works both ways            | Works both ways           |
| On-premises access using VPN or Express Route                              | Works when initiated by pod | Works both ways            | Works both ways           |
| Access to resources secured by service endpoints                           | Supported                  | Supported                  | Supported                 |
| Expose Kubernetes services using a load balancer service, App Gateway, or ingress controller | Supported                  | Supported                  | Supported                 |
| Default Azure DNS and Private Zones                                        | Supported                  | Supported                  | Supported                 |
| Support for Windows node pools                                             | Not Supported              | Supported                  | Supported                 |
| Cluster scale                                                              | 400 nodes and 250 pods/node | 1000 nodes and 250 pods/node | 1000 nodes and 250 pods/node |
| Network configuration                                                      | Complex - requires route tables and UDRs on cluster subnet for pod networking | Simple - no additional configuration required for pod networking | Simple - no additional configuration required for pod networking |
| Pod connectivity performance                                               | Additional hop adds minor latency | Performance on par with VMs in a VNet | Performance on par with VMs in a VNet |
| Kubernetes Network Policies                                                | Calico                     | Azure Network Policies, Calico, Cilium | Calico                    |
| OS platforms supported                                                     | Linux only                 | Linux and Windows Server 2022 | Linux and Windows Server 2022 |
