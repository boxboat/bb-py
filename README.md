# BoxBoat Python Library

`bb-py` is a collection of cloud utilities to simplify deployment in the cloud.

## Installing `bb-py`

#### Prerequisites
* [Python3](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/stable/installing/)
* [pandoc](http://pandoc.org/installing.html)
* [make](https://www.gnu.org/software/make/)


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

#### AWS Execution Note
* All commands assume that you have either [configured credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html) for your currently executing user or your instance is running with an [IAM Instance Profile](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html) associated with it.

### `bb-ec2-auto-tagger`

##### Summary
* Automatically add -0X suffix to EC2 instance Name tag

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
* Dynamically create EC2 [Ansible inventory](http://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) based on generic inventory definition file
* Example definition yaml file below.

##### YAML Definition
* Note `vars` and `children` are optional fields in the `inventory` dictionary.
* You can define `asg_groups` or `ec2_groups` or a mixture as shown in the example

###### Sample Definition

  ```yaml
    ---
    ec2_inventory_groups:
      asg_groups:
        - name: beta-deploy-Masters-AWVW38QQ5V7N-MasterAutoScalingGroup-1Y3LWSEHX9GT
          inventory:
            name: ucp-nodes
            vars:
              - ucp_username: boxboat
              - ucp_password: somepass
        - name: beta-deploy-Workers-Y86UKFTAQ6O9-WorkerAutoScalingGroup-WGI3TXKZMA4U
          inventory:
            name: worker-nodes
            vars:
              - ucp_username: boxboat
              - ucp_password: somepass
            children:
              - dtr_nodes

      ec2_groups:
        - name: beta-dtr-*
          inventory:
            name: dtr-nodes
            vars:
              - ucp_username: boxboat
              - ucp_password: somepass
  ```

###### Sample Output (Passed to Ansible)
* You can preview this output using `--list` as an argument to `bb-ec2-inventory`

  ```json
  {
    "dtr-nodes": {
      "hosts": [
        "10.10.2.125",
        "10.10.4.97",
        "10.10.6.163"
      ]
    },
    "worker-nodes": {
      "hosts": [
        "10.10.4.66",
        "10.10.6.103"
      ],
      "children": [
        "dtr_nodes"
      ]
    },
    "ucp-nodes": {
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

##### File Based Usage
  ```
  INVENTORY_DEFINITION=<path>/file.yaml ansible-playbook -i `which bb-ec2-inventory` playbook.yml
  ```
##### Environment String Based Usage
  ```
  # set the INVENTORY_DEFINITION to a yaml string
  INVENTORY_DEFINITION="
  ec2_inventory_groups:
    asg_groups:
      - name: beta-deploy-Masters-AWVW38QQ5V7N-MasterAutoScalingGroup-1Y3LWSEHX9GT
        inventory:
          name: ucp-nodes
          vars:
            - ucp_username: boxboat
            - ucp_password: somepass
      - name: beta-deploy-Workers-Y86UKFTAQ6O9-WorkerAutoScalingGroup-WGI3TXKZMA4U
        inventory:
          name: worker-nodes
          vars:
            - ucp_username: boxboat
            - ucp_password: somepass
          children:
            - dtr_nodes

    ec2_groups:
      - name: beta-dtr-*
        inventory:
          name: dtr-nodes
          vars:
            - ucp_username: boxboat
            - ucp_password: somepass"
    ansible-playbook -i `which bb-ec2-inventory` playbook.yml
  "
  ```


### `bb-ec2-ssh`

##### Summary
* SSH to ec2 instance forwarding the user SSH key. User is presented with a list of instances to select from that match the search string.


##### Usage
* Default SSH using current user and private ip address

  ```
  bb-ec2-ssh <search>
  ```

* SSH using current user credentials and public ip address (if available)

  ```
  bb-ec2-ssh <search> --public
  ```

* SSH using user foo

  ```
  bb-ec2-ssh <search> --user foo
  ```

### `bb-route53-dns`

#### Summary
* Create A records in private or public hosted zones in Route53. Will automatically get localhost information if running on target EC2 instance. The name used when you are executing locally will be based upon the Name tag for the EC2 instance and it will strip off a Resource tag prefix from that name.
* e.g.
  ```
  Name: foo-bastion-01
  Reource: foo
  Args:
  --public-zone foo.com
  --private-zone foo.internal

  Resulting Route53 entries:
  bastion-01.foo.com
  bastion-01.foo.internal

  With prefix args:
  --private-zone-prefix dev
  --public-zone-prefix dev

  bastion-01.dev.foo.com
  bastion-01.dev.foo.internal

  ```

#### Usage

* Executing on EC2 host you are creating DNS entries for

  ```
  bb-route53-dns --private-zone <private-zone> --public-zone <public-zone --public-zone-prefix <prefix> --private-zone <prefix>
  ```
* Executing on a remote host

  ```
  bb-route53-dns --name <name> --public-ip <public-ip> --private-ip <private-ip> --private-zone <private-zone> --public-zone <public-zone --public-zone-prefix <prefix> --private-zone <prefix>
  ```

### `bb-s3-cp`

##### Summary
* Provides S3 cp commands download, upload and remote copy. If src or destination is a directory will operate recursively.

##### Usage

* Download

  ```
  bb-s3-cp s3://<bucket-name>/<file-key> <local-dest>
  ```

* Upload

  ```
  bb-s3-cp <local-src> s3://<bucket-name>/<file-key>
  ```

* Remote Copy

  ```
  bb-s3-cp s3://<bucket-name>/<file-key> s3://<bucket-name>/<file-key>
  ```


### `bb-vpc-inventory`

##### Summary
* Dynamically create EC2 [Ansible inventory](http://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) for VPC

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
