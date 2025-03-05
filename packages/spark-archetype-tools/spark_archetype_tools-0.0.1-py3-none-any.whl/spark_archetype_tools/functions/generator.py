import requests

class KirbyGen(object):
    def __init__(self, table_raw_name=None, table_master_name=None,
                 token_artifactory=None, outstaging_path=None, is_proxy=False,
                 is_uuaa_tag=False, country="pe", is_ada=False):
        """
                Initialize the KirbyGen class with the given parameters.

                :param table_raw_name: Name of the raw table.
                :param table_master_name: Name of the master table.
                :param token_artifactory: Token for Artifactory authentication.
                :param outstaging_path: Path for outstaging.
                :param is_proxy: Boolean indicating if a proxy should be used.
                :param is_uuaa_tag: Boolean indicating if UUAA tag should be used.
        """
        self.table_raw_name = table_raw_name
        self.table_master_name = table_master_name
        self.table_master_name_l1t = f"{table_master_name}_l1t"
        self.table_master_name_out = f"{table_master_name}_out"
        self.token_artifactory = token_artifactory
        self.outstaging_path = outstaging_path
        self.is_proxy = is_proxy
        self.is_uuaa_tag = is_uuaa_tag
        self.country = country
        self.is_ada = is_ada

        self.session = requests.Session()
        self.current_proxies = {}
        self.text_artifactory = "artifactory"
        self.url_globaldevtools = "globaldevtools.bbva.com"
        self.artifactory_gdt = f"https://{self.text_artifactory}.{self.url_globaldevtools}/{self.text_artifactory}/"

        self.headers = {
            'Content-Type': 'application/json',
            'X-JFrog-Art-Api': f'{token_artifactory}',
            'Authorization': f'{token_artifactory}'
        }
        self.session.headers.update(self.headers)
        if self.is_proxy:
            self.current_proxies = {
                'https': 'http://118.180.54.170:8080',
                'http': 'http://118.180.54.170:8080'
            }
            self.session.proxies.update(self.current_proxies)

        self.repository_initial_path = "${repository.endpoint.vdc}/${repository.repo.schemas}/kirby/" + self.country
        self.repository_version_path = "${version}"

    def kirby_download_schema(self):
        """
        Download the schema for the raw and master tables from Artifactory.
        """

        uuaa_master_name = "".join(self.table_master_name.split("_")[1])

        if self.is_uuaa_tag:
            self.table_raw_name = "".join(self.table_raw_name.split("_")[2:])
            self.table_master_name = "".join(self.table_master_name.split("_")[2:])

        url_raw = f"{self.artifactory_gdt}" \
                  "gl-datio-da-generic-dev-local/" \
                  f"schemas/{self.country}/{uuaa_master_name}/raw/" \
                  f"{self.table_raw_name}/latest/" \
                  f"{self.table_raw_name}.output.schema"
        url_raw_filename = str(url_raw.split("/")[-1])
        path = self.session.get(url_raw)
        with open(url_raw_filename, 'wb') as f:
            f.write(path.content)
        print(f"Download Schema RAWDATA:{url_raw_filename}")

        url_master = f"{self.artifactory_gdt}" \
                     "gl-datio-da-generic-dev-local/" \
                     f"schemas/{self.country}/{uuaa_master_name}/master/" \
                     f"{self.table_master_name}/latest/" \
                     f"{self.table_master_name}.output.schema"
        url_master_filename = str(url_master.split("/")[-1])
        path = self.session.get(url_master)

        with open(url_master_filename, 'wb') as f:
            f.write(path.content)
        print(f"Download Schema MASTERDATA:{url_master_filename}")

    def kirby_formating(self, json_read_file, json_output_file):
        """
        Format the given JSON file to HOCON format and save it to the output file.

        :param json_read_file: Path to the JSON file to read.
        :param json_output_file: Path to the output file to save the formatted HOCON.
        """
        from pyhocon import ConfigFactory
        from pyhocon import HOCONConverter

        conf = ConfigFactory.parse_string(json_read_file)
        hocons_file = HOCONConverter.convert(conf, "hocon")
        with open(json_output_file, "w") as f:
            f.write(hocons_file)
        with open(json_output_file) as f:
            txt_conf = f.read()
        txt_conf = txt_conf.replace('"${?CUTOFF_DATE}"', '${?CUTOFF_DATE}')
        txt_conf = txt_conf.replace('"${?CUTOFF_ODATE}"', '${?CUTOFF_ODATE}')
        txt_conf = txt_conf.replace('"${?AAUUID}"', '${?AAUUID}')
        txt_conf = txt_conf.replace('"${?JOB_NAME}"', '${?JOB_NAME}')
        txt_conf = txt_conf.replace("${CUTOFF_DATE}", '"${?CUTOFF_DATE}"')
        txt_conf = txt_conf.replace("${CUTOFF_ODATE}", '"${?CUTOFF_ODATE}"')
        txt_conf = txt_conf.replace("${AAUUID}", '"${?AAUUID}"')
        txt_conf = txt_conf.replace("${JOB_NAME}", '"${?JOB_NAME}"')
        txt_conf = txt_conf.replace("{PERIOD}", '"${?PERIOD}"')
        txt_conf = txt_conf.replace("/artifactory/", '"/artifactory/"')
        txt_conf = txt_conf.replace('"${ARTIFACTORY_UNIQUE_CACHE}', "${ARTIFACTORY_UNIQUE_CACHE}")
        txt_conf = txt_conf.replace('"${SCHEMAS_REPOSITORY}', '"${SCHEMAS_REPOSITORY}"')

        with open(json_output_file, "w") as f:
            f.write(txt_conf)

    def kirby_conf_input_csv(self):
        """
        Generate the configuration for input CSV files.

        :return: Dictionary containing the configuration for input CSV files.
        """
        from collections import OrderedDict
        uuaa_raw_name = "".join(self.table_raw_name.split("_")[1])
        uuaa_master_name = "".join(self.table_master_name.split("_")[1])
        if self.is_uuaa_tag:
            self.table_raw_name = "".join(self.table_raw_name.split("_")[2:])
            self.table_master_name = "".join(self.table_master_name.split("_")[2:])
        table_dict_conf = OrderedDict(type="csv",
                                      options=dict(delimiter="|", castMode="notPermissive", charset="UTF-8", header=True, overrideSchema=True),
                                      paths=[f"/in/staging/datax/{uuaa_raw_name}/" + "file_{PERIOD}.csv"],
                                      schema=dict(path="")
                                      )
        table_dict_conf["schema"]["path"] = "${ARTIFACTORY_UNIQUE_CACHE}/artifactory/${SCHEMAS_REPOSITORY}" \
                                            f"/schemas/{self.country}/{uuaa_master_name}" \
                                            f"/raw/{self.table_raw_name}/latest/{self.table_raw_name}.output.schema"
        return table_dict_conf

    def kirby_conf_input_table_raw(self, table_name):
        """
        Generate the configuration for input raw tables.

        :param table_name: Name of the raw table.
        :return: Dictionary containing the configuration for input raw tables.
        """
        table_dict_conf = dict(type="table",
                               tables=[f"{self.country}_raw.{table_name}"],
                               options=dict(where="cutoff_date='${CUTOFF_ODATE}'", overrideSchema=True, includeMetadataAndDeleted=True)
                               )
        return table_dict_conf

    def kirby_conf_input_table_master(self, table_name):
        """
        Generate the configuration for input master tables.

        :param table_name: Name of the master table.
        :return: Dictionary containing the configuration for input master tables.
        """
        table_dict_conf = dict(type="table",
                               tables=[f"{self.country}_master.{table_name}"],
                               options=dict(where="cutoff_date='${CUTOFF_DATE}'", overrideSchema=True, includeMetadataAndDeleted=True)
                               )
        return table_dict_conf

    def kirby_conf_output_table(self, table_name, table_type):
        """
        Generate the configuration for output tables.

        :param table_name: Name of the output table.
        :param table_type: Type of the table (raw or master).
        :return: Dictionary containing the configuration for output tables.
        """
        from collections import OrderedDict
        table_format = ""
        if table_type == "raw":
            table_format = "avro"
        elif table_type == "master":
            table_format = "parquet"
        table_dict_conf = OrderedDict(type="table",
                                      table=f"{self.country}_{table_type}.{table_name}",
                                      castTypes=True,
                                      mode="overwrite",
                                      options=dict(partitionOverwriteMode="dynamic", keepPermissions=True),
                                      force=True,
                                      dropLeftoverFields=True,
                                      partition=["cutoff_date"],
                                      compact=True,
                                      compactConfig=dict(forceTargetPathRemove=True, partitionDiscovery=True, report=True, tableFormat=table_format)
                                      )
        return table_dict_conf

    def kirby_conf_output_csv(self, outstaging_path):
        """
        Generate the configuration for output CSV files.

        :param outstaging_path: Path for outstaging.
        :return: Dictionary containing the configuration for output CSV files.
        """
        from collections import OrderedDict
        table_dict_conf = OrderedDict(type="csv",
                                      path=outstaging_path,
                                      castTypes=True,
                                      mode="overwrite",
                                      options=dict(delimiter="|", castMode="notPermissive", charset="UTF-8", header=True, keepPermissions=True, overrideSchema=True),
                                      force=True,
                                      dropLeftoverFields=True,
                                      coalesce=dict(partitions=1)
                                      )
        return table_dict_conf

    def kirby_conf_transform_table_raw(self):
        """
        Generate the transformation configuration for raw tables.

        :return: List containing the transformation configuration for raw tables.
        """
        from collections import OrderedDict
        table_list_conf = list()

        literal_dict = OrderedDict()
        literal_dict["type"] = "literal"
        literal_dict["field"] = "cutoff_date"
        literal_dict["default"] = "${?CUTOFF_ODATE}"
        literal_dict["defaultType"] = "string"

        set_currentdate_dict = OrderedDict()
        set_currentdate_dict["type"] = "setCurrentDate"
        set_currentdate_dict["field"] = "audtiminsert_date"

        formatter_dict = OrderedDict()
        formatter_dict["type"] = "formatter"
        formatter_dict["field"] = "audtiminsert_date"
        formatter_dict["typeToCast"] = "string"

        table_list_conf.append(literal_dict)
        table_list_conf.append(set_currentdate_dict)
        table_list_conf.append(formatter_dict)

        return table_list_conf

    def kirby_conf_transform_table_master(self):
        """
        Generate the transformation configuration for master tables.

        :return: List containing the transformation configuration for master tables.
        """
        from collections import OrderedDict
        import json

        table_list_conf = list()

        with open(f"{self.table_master_name}.output.schema") as f:
            txt_conf = f.read()
        txt_json = json.loads(txt_conf)

        rename_col_dict = dict()
        rename_columns_list = list()
        trim_columns_list = list()
        decimal_columns_list = list()
        date_columns_list = list()
        int_columns_list = list()
        timestamp_columns_list = list()
        all_columns_list = list()
        global _decimal_columns, _date_columns, _int_columns, _timestamp_columns

        for field in txt_json["fields"]:
            name = field.get("name")
            legacy_name = field.get("legacyName")
            logical_format = field.get("logicalFormat")
            all_columns_list.append(name)
            if str(name).lower() not in ("audtiminsert_date", "cutoff_date"):
                if not str(legacy_name).startswith("calculated") or len(str(legacy_name).split(";")) > 1:
                    trim_columns_list.append(legacy_name)
                    rename_col_dict[legacy_name] = name
                if str(logical_format).upper().startswith("DECIMAL"):
                    decimal_columns_list.append(name)
                if str(logical_format).upper().startswith("DATE"):
                    date_columns_list.append(name)
                if str(logical_format).upper().startswith(("INT", "NUMERIC")):
                    int_columns_list.append(name)
                if str(logical_format).upper().startswith("TIMESTAMP"):
                    timestamp_columns_list.append(name)

        rename_columns_list.append(rename_col_dict)
        trim_columns = "|".join(trim_columns_list)

        sqlfilter_dict = OrderedDict()
        sqlfilter_dict["type"] = "sqlFilter"
        sqlfilter_dict["filter"] = "cutoff_date='${CUTOFF_ODATE}'"

        trim_dict = dict()
        trim_dict["type"] = "trim"
        trim_dict["field"] = trim_columns
        trim_dict["regex"] = True
        trim_dict["trimType"] = "both"

        renamecol_dict = dict()
        renamecol_dict["type"] = "renamecolumns"
        renamecol_dict["columnsToRename"] = rename_col_dict

        run_id_dict = OrderedDict()
        run_id_dict["type"] = "literal"
        run_id_dict["field"] = "gf_run_id"
        run_id_dict["default"] = "${?AAUUID}"
        run_id_dict["defaultType"] = "string"

        job_name_dict = OrderedDict()
        job_name_dict["type"] = "literal"
        job_name_dict["field"] = "gf_user_audit_id"
        job_name_dict["default"] = "${?JOB_NAME}"
        job_name_dict["defaultType"] = "string"

        formatter_decimal_dict = dict()
        if len(decimal_columns_list) > 0:
            _decimal_columns = "|".join(decimal_columns_list)
            formatter_decimal_dict["type"] = "formatter"
            formatter_decimal_dict["field"] = _decimal_columns
            formatter_decimal_dict["regex"] = True
            formatter_decimal_dict["typeToCast"] = "decimal(23,10)"

        formatter_date_dict = dict()
        if len(date_columns_list) > 0:
            _date_columns = "|".join(date_columns_list)
            formatter_date_dict["type"] = "formatter"
            formatter_date_dict["field"] = _date_columns
            formatter_date_dict["regex"] = True
            formatter_date_dict["typeToCast"] = "date"

        formatter_int_dict = dict()
        if len(int_columns_list) > 0:
            _int_columns = "|".join(int_columns_list)
            formatter_int_dict["type"] = "formatter"
            formatter_int_dict["field"] = _int_columns
            formatter_int_dict["regex"] = True
            formatter_int_dict["typeToCast"] = "integer"

        formatter_timestamp_dict = dict()
        if len(timestamp_columns_list) > 0:
            _timestamp_columns = "|".join(timestamp_columns_list)
            formatter_timestamp_dict["type"] = "formatter"
            formatter_timestamp_dict["field"] = _timestamp_columns
            formatter_timestamp_dict["regex"] = True
            formatter_timestamp_dict["typeToCast"] = "timestamp"

        literal_dict = dict()
        literal_dict["type"] = "literal"
        literal_dict["field"] = "cutoff_date"
        literal_dict["default"] = "${?CUTOFF_DATE}"
        literal_dict["defaultType"] = "string"

        setcurrentdate_dict = dict()
        setcurrentdate_dict["type"] = "setCurrentDate"
        setcurrentdate_dict["field"] = "audtiminsert_date"

        formatter2_dict = dict()
        formatter2_dict["type"] = "formatter"
        formatter2_dict["field"] = "cutoff_date"
        formatter2_dict["regex"] = True
        formatter2_dict["replacements"] = []
        formatter2_dict["typeToCast"] = "date"

        formatter_dict = dict()
        formatter_dict["type"] = "formatter"
        formatter_dict["field"] = "audtiminsert_date"
        formatter_dict["replacements"] = []
        formatter_dict["typeToCast"] = "timestamp"

        selectcolumns_dict = dict()
        selectcolumns_dict["type"] = "selectcolumns"
        selectcolumns_dict["columnsToSelect"] = all_columns_list

        table_list_conf.append(sqlfilter_dict)
        table_list_conf.append(trim_dict)
        table_list_conf.append(renamecol_dict)
        if len(decimal_columns_list) > 0:
            table_list_conf.append(formatter_decimal_dict)
        if len(date_columns_list) > 0:
            table_list_conf.append(formatter_date_dict)
        if len(int_columns_list) > 0:
            table_list_conf.append(formatter_int_dict)
        if len(timestamp_columns_list) > 0:
            table_list_conf.append(formatter_timestamp_dict)

        table_list_conf.append(literal_dict)
        table_list_conf.append(setcurrentdate_dict)
        table_list_conf.append(formatter2_dict)
        table_list_conf.append(formatter_dict)
        table_list_conf.append(selectcolumns_dict)

        return table_list_conf

    def kirby_conf_transform_table_master_l1t(self):
        """
        Generate the transformation configuration for master L1T tables.

        :return: List containing the transformation configuration for master L1T tables.
        """
        from collections import OrderedDict
        import json

        table_list_conf = list()

        sqlfilter_dict = OrderedDict()
        sqlfilter_dict["type"] = "sqlFilter"
        sqlfilter_dict["filter"] = "cutoff_date='${CUTOFF_DATE}'"

        preserve_order_dict = dict()
        preserve_order_dict["type"] = "preserveorder"

        table_list_conf.append(sqlfilter_dict)
        table_list_conf.append(preserve_order_dict)

        return table_list_conf

    def kirby_conf_transform_table_outstaging(self):
        """
        Generate the transformation configuration for outstaging tables.

        :return: List containing the transformation configuration for outstaging tables.
        """

        from collections import OrderedDict
        import json

        table_list_conf = list()

        with open(f"{self.table_master_name}.output.schema") as f:
            txt_conf = f.read()
        txt_json = json.loads(txt_conf)

        trim_columns_list = list()
        all_columns_list = list()
        for field in txt_json["fields"]:
            name = field.get("name")
            all_columns_list.append(name)
            trim_columns_list.append(name)

        trim_columns = "|".join(trim_columns_list)

        sqlfilter_dict = OrderedDict()
        sqlfilter_dict["type"] = "sqlFilter"
        sqlfilter_dict["filter"] = "cutoff_date='${CUTOFF_DATE}'"

        trim_dict = dict()
        trim_dict["type"] = "trim"
        trim_dict["field"] = trim_columns
        trim_dict["regex"] = True
        trim_dict["trimType"] = "both"

        selectcolumns_dict = dict()
        selectcolumns_dict["type"] = "selectcolumns"
        selectcolumns_dict["columnsToSelect"] = all_columns_list

        table_list_conf.append(sqlfilter_dict)
        table_list_conf.append(trim_dict)
        table_list_conf.append(selectcolumns_dict)
        return table_list_conf

    def generate_kirby_conf_raw(self):
        import json
        table_dict_conf = dict()
        table_dict_conf[self.table_master_name] = dict(kirby=dict(input=dict(),
                                                                  output=dict(),
                                                                  transformations=list()))
        _input = self.kirby_conf_input_csv()
        _output = self.kirby_conf_output_table(table_name=self.table_raw_name, table_type="raw")
        _transform = self.kirby_conf_transform_table_raw()
        table_dict_conf[self.table_master_name]["kirby"]["input"] = _input
        table_dict_conf[self.table_master_name]["kirby"]["output"] = _output
        table_dict_conf[self.table_master_name]["kirby"]["transformations"] = _transform

        txt_string = table_dict_conf[self.table_master_name]
        json_file = json.dumps(txt_string, indent=4)
        self.kirby_formating(json_read_file=json_file, json_output_file=f"{self.table_raw_name}.conf")

        if self.is_ada:
            self.generate_kirby_ada_json(table_type="raw")
        else:
            self.generate_kirby_json(table_type="raw")

    def generate_kirby_conf_master(self):
        import json
        table_dict_conf = dict()
        table_dict_conf[self.table_master_name] = dict(kirby=dict(input=dict(),
                                                                  output=dict(),
                                                                  transformations=list()))
        _input = self.kirby_conf_input_table_raw(table_name=self.table_raw_name)
        _output = self.kirby_conf_output_table(table_name=self.table_master_name, table_type="master")
        _transform = self.kirby_conf_transform_table_master()
        table_dict_conf[self.table_master_name]["kirby"]["input"] = _input
        table_dict_conf[self.table_master_name]["kirby"]["output"] = _output
        table_dict_conf[self.table_master_name]["kirby"]["transformations"] = _transform

        txt_string = table_dict_conf[self.table_master_name]
        json_file = json.dumps(txt_string, indent=4)
        self.kirby_formating(json_read_file=json_file, json_output_file=f"{self.table_master_name}.conf")
        if self.is_ada:
            self.generate_kirby_ada_json(table_type="master")
        else:
            self.generate_kirby_json(table_type="master")

    def generate_kirby_conf_master_l1t(self):
        import json
        table_dict_conf = dict()
        table_dict_conf[self.table_master_name] = dict(kirby=dict(input=dict(),
                                                                  output=dict(),
                                                                  transformations=list()))
        _input = self.kirby_conf_input_table_master(table_name=self.table_master_name)
        _output = self.kirby_conf_output_table(table_name=f"{self.table_master_name_l1t}", table_type="master")
        _transform = self.kirby_conf_transform_table_master_l1t()
        table_dict_conf[self.table_master_name]["kirby"]["input"] = _input
        table_dict_conf[self.table_master_name]["kirby"]["output"] = _output
        table_dict_conf[self.table_master_name]["kirby"]["transformations"] = _transform

        txt_string = table_dict_conf[self.table_master_name]
        json_file = json.dumps(txt_string, indent=4)
        self.kirby_formating(json_read_file=json_file, json_output_file=f"{self.table_master_name_l1t}.conf")
        if self.is_ada:
            self.generate_kirby_ada_json(table_type="master_l1t")
        else:
            self.generate_kirby_json(table_type="master_l1t")

    def generate_kirby_conf_outstaging(self):
        import json
        table_dict_conf = dict()
        table_dict_conf[self.table_master_name] = dict(kirby=dict(input=dict(),
                                                                  output=dict(),
                                                                  transformations=list()))
        _input = self.kirby_conf_input_table_master(table_name=self.table_master_name)
        _output = self.kirby_conf_output_csv(outstaging_path=self.outstaging_path)
        _transform = self.kirby_conf_transform_table_outstaging()
        table_dict_conf[self.table_master_name]["kirby"]["input"] = _input
        table_dict_conf[self.table_master_name]["kirby"]["output"] = _output
        table_dict_conf[self.table_master_name]["kirby"]["transformations"] = _transform

        txt_string = table_dict_conf[self.table_master_name]
        json_file = json.dumps(txt_string, indent=4)
        self.kirby_formating(json_read_file=json_file, json_output_file=f"{self.table_master_name_out}.conf")
        if self.is_ada:
            self.generate_kirby_ada_json(table_type="master_out")
        else:
            self.generate_kirby_json(table_type="master_out")

    def generate_kirby_json(self, table_type):
        from collections import OrderedDict
        import json

        uuaa_master = "".join(self.table_master_name.split("_")[1])
        uuaa_tag_master = "".join(self.table_master_name.split("_")[2:])
        job_name = ""
        json_output_file = ""
        repo_config = ""

        if table_type == "raw":
            job_name = f"{uuaa_master}-{self.country}-krb-inr-{uuaa_tag_master}"
            env = {"XD_ENABLED": "true"}
            tags = ["RAW_INGESTION", f"{uuaa_master.upper()}"]
            json_output_file = f"{self.table_raw_name}.json"
            repo_config = f"{self.repository_initial_path}/{uuaa_master}/raw/{self.table_raw_name}/{self.repository_version_path}/{self.table_raw_name}.conf"
        elif table_type == "master":
            job_name = f"{uuaa_master}-{self.country}-krb-inm-{uuaa_tag_master}"
            env = {"XD_ENABLED": "true"}
            tags = ["MASTER_INGESTION", f"{uuaa_master.upper()}"]
            json_output_file = f"{self.table_master_name}.json"
            repo_config = f"{self.repository_initial_path}/{uuaa_master}/master/{self.table_master_name}/{self.repository_version_path}/{self.table_master_name}.conf"
        elif table_type == "master_l1t":
            job_name = f"{uuaa_master}-{self.country}-krb-inm-{uuaa_tag_master}l1t"
            env = {"XD_ENABLED": "true"}
            tags = ["MASTERL1T_INGESTION", f"{uuaa_master.upper()}"]
            json_output_file = f"{self.table_master_name_l1t}.json"
            repo_config = f"{self.repository_initial_path}/{uuaa_master}/master/{self.table_master_name_l1t}/{self.repository_version_path}/{self.table_master_name_l1t}.conf"
        elif table_type == "master_out":
            job_name = f"{uuaa_master}-{self.country}-krb-inm-{uuaa_tag_master}out"
            env = {"XD_ENABLED": "true"}
            tags = ["MASTEROUT_INGESTION", f"{uuaa_master.upper()}"]
            json_output_file = f"{self.table_master_name_out}.json"
            repo_config = f"{self.repository_initial_path}/{uuaa_master}/master/{self.table_master_name_out}/{self.repository_version_path}/{self.table_master_name_out}.conf"

        table_dict = OrderedDict(
            _id=f"{job_name}p-01",
            description=f"Job {job_name}p-01 created with Skynet.",
            kind="processing",
            params=dict(configUrl=f"{repo_config}", sparkHistoryEnabled="false"),
            env=env,
            runtime="kirby3-lts",
            size="M",
            tags=tags,
            streaming=False,
            concurrency=49)
        json_file = json.dumps(table_dict, indent=4)
        with open(json_output_file, "w") as f:
            f.write(json_file)

    def generate_kirby_ada_json(self, table_type):
        from collections import OrderedDict
        import json

        uuaa_master = "".join(self.table_master_name.split("_")[1])
        uuaa_tag_master = "".join(self.table_master_name.split("_")[2:])
        job_name = ""
        json_output_file = ""

        if table_type == "raw":
            job_name = f"{uuaa_master}-{self.country}-krb-inr-{uuaa_tag_master}"
            env = {"XD_ENABLED": "true"}
            tags = ["RAW_INGESTION", f"{uuaa_master.upper()}"]
            json_output_file = f"{self.table_raw_name}.json"
        elif table_type == "master":
            job_name = f"{uuaa_master}-{self.country}-krb-inm-{uuaa_tag_master}"
            env = {"XD_ENABLED": "true"}
            tags = ["MASTER_INGESTION", f"{uuaa_master.upper()}"]
            json_output_file = f"{self.table_master_name}.json"

        elif table_type == "master_l1t":
            job_name = f"{uuaa_master}-{self.country}-krb-inm-{uuaa_tag_master}l1t"
            env = {"XD_ENABLED": "true"}
            tags = ["MASTERL1T_INGESTION", f"{uuaa_master.upper()}"]
            json_output_file = f"{self.table_master_name_l1t}.json"
        elif table_type == "master_out":
            job_name = f"{uuaa_master}-{self.country}-krb-inm-{uuaa_tag_master}out"
            env = {"XD_ENABLED": "true"}
            tags = ["MASTEROUT_INGESTION", f"{uuaa_master.upper()}"]
            json_output_file = f"{self.table_master_name_out}.json"

        table_dict = OrderedDict(
            _id=f"{job_name}p-01",
            description=f"Job {job_name}p-01 created with Skynet.",
            kind="processing",
            params=dict(metaConfig=f"{self.country}:{uuaa_master}:migration:{job_name}p-01:0.0.1-migration", sparkHistoryEnabled="false"),
            env=env,
            runtime="kirby3-lts",
            size="M",
            tags=tags,
            streaming=False,
            concurrency=49)
        json_file = json.dumps(table_dict, indent=4)
        with open(json_output_file, "w") as f:
            f.write(json_file)