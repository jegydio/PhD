# PSI5120 - Avaliação intermediária


Este trabalho tem como objetivo implementar um servidor web em um cluster Kubernetes com autoescalonamento horizontal automático. Primeiramente, implementaremos usando o minikube e, em seguida, utilizaremos o AWS EKS.

## Resumo

### 1. Executando o Cluster Kubernetes usando Minikube

1.1 [Instalando o metrics-server](#1.1)

1.2 [Iniciando o Minikube e habilitando o metrics-server](#1.2)

1.3 [Executando e expondo o servidor php-apache](#1.3)

1.4 [Criando o HorizontalPodAutoscaler](#1.4)

1.5 [Aumentando a carga](#1.5)

1.6 [Parando a carga](#1.6)

### 2. Cluster AWS EKS

2.1 [Criando o Cluster EKS](#2.1)

2.2 [Executando o HorizontalPodAutoscaler](#2.2)

## 1. Executando o Cluster Kubernetes usando Minikube <a name="1."></a>

## Pré-requisitos

- [Docker](https://docs.docker.com/engine/install/)

- [Minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Fbinary+download)

- [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) (versão 1.23 ou superior)

### 1.1 Instalando o metrics-server <a name="1.1"></a>

Primeiramente, delete o Metrics Server existente, se houver algum.

```console
$ kubectl delete -n kube-system deployments.apps metrics-server
```

Instale a partir do GitHub com o seguinte comando.

```console
$ wget https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.5.0/components.yaml
```

Para comunicação segura, é necessário editar o arquivo components.yaml. Selecione a parte "Deployment" no arquivo. Adicione a linha abaixo ao campo "containers.args" no objeto deployment.

```console
- --kubelet-insecure-tls
```

Após a modificação, o arquivo ficará assim:

```console
spec:
      containers:
      - args:
        - --cert-dir=/tmp
        - --secure-port=443
        - --kubelet-insecure-tls
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
```

Adicionando o "metrics-server" à sua instância Kubernetes.

```console
kubectl apply -f components.yaml
```

Após 1-2 minutos, verifique a existência do metrics-server, executando o comando:

```console
$ kubectl -n kube-system get pods
```

Para verificar se o "metrics-server" pode acessar os recursos dos pods e nós, você pode executar os seguintes comandos:

```console
$ kubectl top pods
$ kubectl top nodes
```

Se os valores de métricas, sob a coluna "current", forem números e não "unknown", está tudo correto.

### 1.2 Iniciando o Minikube e habilitando o metrics-server <a name="1.2"></a>

Agora, é necessário iniciar o minikube. São necessários pelo menos dois nós. Portanto, você precisa usar o seguinte comando:

```console
$ minikube start --nodes 2 -p multinode-demo
```

Para obter a lista de nós, você pode usar o comando:

```console
$ kubectl get nodes
```

Para habilitar o metrics-server, você deve usar o seguinte comando:

```console
$ minikube addons enable metrics-server
```

### 1.3 Executando e expondo o servidor php-apache <a name="1.3"></a>

Para demonstrar um HorizontalPodAutoscaler, você deve primeiro iniciar um Deployment que executa um contêiner usando a imagem hpa-example e expô-lo como um Serviço usando o seguinte manifesto:

Execute o seguinte comando para executar um contêiner usando a imagem hpa-example e expô-lo como um Serviço:

```console
$ kubectl apply -f https://k8s.io/examples/application/php-apache.yaml
```

Você pode ver o php-apache.yaml neste repositório.

### 1.4 Criando o HorizontalPodAutoscaler <a name="1.4"></a>

Depois que o servidor estiver em execução, é necessário criar o autoscaler usando o kubectl. Vamos criar o HorizontalPodAutoscaler executando o comando abaixo:

```console
$ kubectl autoscale deployment php-apache --cpu-percent=50 --min=1 --max=10
```

Você pode verificar o status atual do HorizontalPodAutoscaler com o comando:

```console
$ kubectl get hpa
```

A saída será algo como abaixo:

```console
NAME         REFERENCE               TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache   cpu: 0%/50%   1         10        1          159m
```

### 1.5 Aumentando a carga <a name="1.5"></a>

Para ver o autoscaler reagir, você abrirá um terminal diferente e executará o comando abaixo:

```console
$ kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://php-apache; done"
```

Depois de um minuto, você pode executar o comando:

```console
$ kubectl get hpa php-apache --watch
```

Você verá abaixo de "TARGET" a porcentagem mais alta, e o número de "REPLICAS" também aumentará.

### 1.6 Parando a carga <a name="1.6"></a>

No terminal em que você executou o gerador de carga, você precisa pressionar \<ctrl> + c para parar.

Depois você pode executar o comando:

```console
$ kubectl get hpa php-apache --watch
```

Então, você verá a porcentagem abaixo de "TARGET" diminuindo para zero.

## 2. Cluster AWS EKS <a name="2."></a>

## Pré-requisitos

- [eksctl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html#eksctl-install-update)

- [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) (versão 1.23 ou superior)

- [Instalando AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

- [Configurar AWS CLI](https://docs.aws.amazon.com/eks/latest/userguide/install-awscli.html)

- [Criar Cluster EKS](#2.1)

- [Metrics Server](#1.2)

### 2.1 Criando o Cluster EKS <a name="2.1"></a>

Primeiramente, você precisa criar uma função (role). Na sua conta AWS, procure por **Elastic Kubernetes Service**. Clique em "Adicionar cluster" e configure conforme abaixo:

- Nome do cluster: eks_cluster
- Rede VPC: Padrão
- Subnets: east-us-1a, east-us-1b, east-us-1c
- Grupo de segurança: Padrão

Agora, criaremos um grupo de nós. No cluster que você acabou de criar, vá para "Compute", clique em "Adicionar grupo de nós" e configure conforme abaixo:

- Nome: eks_node_group_1
- Função IAM dos nós: Crie uma com o nome eks_workers_role
- Tipo de instância: t3.medium

Depois disso, configuraremos o cluster. Use a sequência de comandos abaixo:

```console
$ aws sts get-caller-identity
$ aws eks update-kubeconfig --region us-east-1 --name eks_cluster
```

É necessário configurar o nginx. Dentro deste repositório, há um arquivo chamado nginx-deployment.yaml. Para implantar, use o comando:

```console
$ kubectl apply -f nginx-deployment.yaml
```

Execute o comando abaixo para expor o deployment do Nginx como um serviço LoadBalancer.

```console
$ kubectl expose deployment nginx-deployment --name=nginx-service --port=80 --target-port=80 --type=LoadBalancer
```

Para ver informações sobre o serviço Nginx com LoadBalancer, execute o comando abaixo:

```console
$ kubectl get service nginx-service
```

### 2.2 Executando o HorizontalPodAutoscaler <a name="2.2"></a>

Depois de configurar o Cluster EKS no seu dispositivo local, você pode fazer o mesmo procedimento do tópico [1.3 Executando e expondo o servidor php-apache](#1.3)

### REFERÊNCIAS

Documentação do Kubernetes. (s.d.). Passo a passo do Horizontal Pod Autoscale. Acessado em 4 de agosto de 2024, de https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/

Amazon Web Services. (s.d.). Horizontal Pod Autoscaler. Acessado em 4 de agosto de 2024, de https://docs.aws.amazon.com/eks/latest/userguide/horizontal-pod-aut