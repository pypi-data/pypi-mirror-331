# spark_archetype_tools

[![Github License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Updates](https://pyup.io/repos/github/woctezuma/google-colab-transfer/shield.svg)](pyup)
[![Python 3](https://pyup.io/repos/github/woctezuma/google-colab-transfer/python-3-shield.svg)](pyup)
[![Code coverage](https://codecov.io/gh/woctezuma/google-colab-transfer/branch/master/graph/badge.svg)](codecov)

spark_archetype_tools is a Python library that implements jira task

## Installation

The code is packaged for PyPI, so that the installation consists in running:

## Usage

wrapper run jira task

## Sandbox

## Installation

```sh
!yes| pip uninstall spark-archetype-tools
```

```sh
pip install spark-archetype-tools --user --upgrade
```

## IMPORTS

```sh
from spark_archetype_tools import KirbyGen

```

## Variables

```sh
table_raw_name = "t_klau_recndct_cst_crdc_ctr_eval"
table_master_name = "t_psan_recndct_cst_crdc_ctr_eval"
outstaging_path = "/out/staging/ratransmit/psan/t_psan_recndct_cst_crdc_ctr_eval"
token_artifactory = "XXXXXXXXX"
is_proxy  = False
country = "pe"
is_uuaa_tag = False
```


## KirbyGen

```sh
kirby_gen = KirbyGen(table_raw_name=table_raw_name, 
                     table_master_name=table_master_name,
                     token_artifactory=token_artifactory,
                     outstaging_path=outstaging_path,
                     is_proxy=is_proxy,
                     is_uuaa_tag=is_uuaa_tag,
                     country=country)
                     
 kirby_gen.kirby_download_schema()                                         
 kirby_gen.generate_kirby_conf_raw()
 kirby_gen.generate_kirby_conf_master()
 kirby_gen.generate_kirby_conf_master_l1t() 
 kirby_gen.generate_kirby_conf_outstaging()                    
```

## Show Code Template
1. Kirby
2. Hammurabi
3. Scala
4. Scaffolder


## Structure
```sh

```




## License

[Apache License 2.0](https://www.dropbox.com/s/8t6xtgk06o3ij61/LICENSE?dl=0).

## New features v1.0

## BugFix

- choco install visualcpp-build-tools

## Reference

- Jonathan Quiza [github](https://github.com/jonaqp).
- Jonathan Quiza [RumiMLSpark](http://rumi-ml.herokuapp.com/).
