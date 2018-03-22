# BoxBoat Python Library

`bb-py` is a collection of cloud utilities to simplify deployment in the cloud.

## Installing `bb-py`

#### Prerequisites
* python
* pip
* make

#### Build
1. Checkout release from gitlab
2. `cd bb-py`
3. `make`
  * Creates:
    * `dist/bb_py<version>.whl`
    * `bb-py.tgz` (archive of `dist/`)


#### Installation
`pip install bb_py-<version>.whl`

## Installed Commands

### `bb-ec2-auto-tagger`
# Automatically add -0X suffix to EC2 instance Name tag

##### Usage
* Execute on non AutoScalingGroup instance by providing basename
  ```
  bb-ec2-auto-tagger --basename <ec2-instance-basename> --region <aws-region>
  ```
* Execute on AutoScalingGroup instance
  ```
  bb-ec2-auto-tagger --region <aws-region>
  ```

### `bb-ec2-inventory`

##### Summary
* Dynamically create EC2 Ansible inventory based on generic inventory definition file
* Example definition yaml file below.

##### YAML Definition File
* Note `vars` and `children` are optional fields in the `inventory` dictionary.
* You can define `asg_groups` or `ec2_groups` or a mixture as shown in the example

###### Sample Definition
  ```yaml
    ---
    ec2_inventory_groups:
      asg_groups:
        - name: beta-deploy-Masters-AWVW38QQ5V7N-MasterAutoScalingGroup-1Y3LWSEHX9GT
          inventory:
            name: ucp_nodes
            vars:
              - ucp_username: boxboat
              - ucp_password: somepass
        - name: beta-deploy-Workers-Y86UKFTAQ6O9-WorkerAutoScalingGroup-WGI3TXKZMA4U
          inventory:
            name: ucp_workers
            vars:
              - ucp_username: boxboat
              - ucp_password: somepass
            children:
              - dtr_nodes

      ec2_groups:
        - name: beta-dtr-*
          inventory:
            name: dtr_nodes
            vars:
              - ucp_username: boxboat
              - ucp_password: somepass
  ```
###### Sample Output (Passed to Ansible)
* You can preview this output using `--list` as an argument to `bb-ec2-inventory`
  
  ```json
  {
    "dtr_nodes": {
      "hosts": [
        "10.10.2.125",
        "10.10.4.97",
        "10.10.6.163"
      ]
    },
    "ucp_workers": {
      "hosts": [
        "10.10.4.66",
        "10.10.6.103"
      ],
      "children": [
        "dtr_nodes"
      ]
    },
    "ucp_nodes": {
      "hosts": [
        "10.10.4.109",
        "10.10.2.130",
        "10.10.6.161"
      ]
    },
    "_meta": {
      "hostvars": {
        "10.10.6.163": {
          "ucp_password": "somepass",
          "ucp_username": "boxboat"
        },
        "10.10.6.161": {
          "ucp_password": "somepass",
          "ucp_username": "boxboat"
        },
        "10.10.2.130": {
          "ucp_password": "somepass",
          "ucp_username": "boxboat"
        },
        "10.10.2.125": {
          "ucp_password": "somepass",
          "ucp_username": "boxboat"
        },
        "10.10.4.97": {
          "ucp_password": "somepass",
          "ucp_username": "boxboat"
        },
        "10.10.4.109": {
          "ucp_password": "somepass",
          "ucp_username": "boxboat"
        },
        "10.10.6.103": {
          "ucp_password": "somepass",
          "ucp_username": "boxboat"
        },
        "10.10.4.66": {
          "ucp_password": "somepass",
          "ucp_username": "boxboat"
        }
      }
    }
  }
  ```
##### Usage
  ```
  INVENTORY_FILE=<path>/file.yaml ansible-playbook -i `which bb-ec2-inventory` playbook.yml
  ```


### `bb-vpc-inventory`

##### Summary
* Dynamically create EC2 Ansible inventory for VPC

###### Sample Output (Passed to Ansible)
* You can preview this output using `--list` as an argument to `bb-ec2-inventory`

  ```json
  {
    "vpc_inventory": {
      "hosts": [
        "10.10.4.66",
        "10.10.1.103",
        "10.10.2.125",
        "10.10.4.97",
        "10.10.4.109",
        "10.10.2.130",
        "10.10.6.163",
        "10.10.6.161",
        "10.10.6.103"
      ]
    },
    "_meta": {
      "hostvars": {}
    }
  }
  ```

##### Usage
* Using VPC name
  ```
  VPC_NAME=<vpc-name> ansible-playbook -i `which bb-vpc-inventory` playbook.yml
  ```
* Using VPC id
  ```
  VPC_ID=<vpc-id> ansible-playbook -i `which bb-vpc-inventory` playbook.yml
  ```
