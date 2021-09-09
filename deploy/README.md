### Deploy vars

See variable defaults in our ansible [playbook](https://github.com/lionbridgeai/ai-dev-tools/blob/master/ansible-plays/roles/create_k8s_resources/vars/main.yml)

See order of precedence (highest to lowest):
 - .env (only when using `make up` and only if also present in docker-compose.yml)
 - ./{env.yml}
 - ./common.yml
 - roles/create_k8s_resources/vars/main.yml in [ansible playbook](https://github.com/lionbridgeai/ai-dev-tools/blob/master/ansible-plays/roles/create_k8s_resources/vars/main.yml)
