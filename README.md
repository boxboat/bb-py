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
