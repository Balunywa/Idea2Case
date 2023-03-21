

| Network Model    | When to use                                                                                                        |
| ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| Kubenet          | - IP address space conservation is a priority<br>- Simple configuration<br>- Fewer than 400 nodes per cluster<br>- Kubernetes internal or external load balancers sufficient for reaching pods from outside the cluster<br>- Manually managing and maintaining user-defined routes is acceptable |
| Azure CNI        | - Full virtual network connectivity is required for pods<br>- Advanced AKS features (such as virtual nodes) are needed<br>- Sufficient IP address space is available<br>- Pod to pod and pod to VM connectivity needed<br>- External resources need to reach pods directly<br>- AKS network policies are required |
| Azure CNI Overlay | - IP address shortage is a concern<br>- Scaling up to 1000 nodes and 250 pods per node is sufficient<br>- Additional hop for pod connectivity is acceptable<br>- Complex network configuration is not a barrier<br>- AKS egress requirements can be met |

