from sigma.pipelines.base import Pipeline
from sigma.processing.transformations import (
    AddConditionTransformation,
    FieldMappingTransformation,
)

from sigma.processing.conditions import LogsourceCondition
from sigma.processing.pipeline import ProcessingItem, ProcessingPipeline

ocsf_generic_logsource_mapping = {  # map generic Sigma log sources to OCSF Categories and Activities
    "application": {
        "class_uid": 6002,
        "category_uid": 6,
    },
    "antivirus": {
        "class_uid": 2004,
        "category_uid": 2,
    },
    # "clipboard_capture": 24,
    # "create_remote_thread": 8,
    "create_stream_hash": {"class_uid": 1001, "category_uid": 1, "activity_id": 3},
    "dns": {"class_uid": 4003, "category_uid": 4},
    "dns_query": {"class_uid": 4003, "category_uid": 4},
    "driver_load": {
        "class_uid": 1007,
        "category_uid": 1,
        "activity_id": 2,
    },
    "firewall": {"class_uid": 4001, "category_uid": 4},
    "file_access": {"class_uid": 1001, "category_uid": 1, "activity_id": 14},
    "file_change": {"class_uid": 1001, "category_uid": 1, "activity_id": 3},
    "file_delete": {"class_uid": 1001, "category_uid": 1, "activity_id": 4},
    "file_event": {"class_uid": 1001, "category_uid": 1, "activity_id": 1},
    "file_executable_detected": {"class_uid": 1001, "category_uid": 1, "activity_id": 1},
    "file_rename": {"class_uid": 1001, "category_uid": 1, "activity_id": 5},
    "image_load": {
        "class_uid": 1007,
        "category_uid": 1,
        "activity_id": 99,
        "activity_name": "Load",
    },
    "network_connection": {"class_uid": 4001, "category_uid": 4},
    # "pipe_created": [17, 18],
    "process_access": {
        "class_uid": 1007,
        "category_uid": 1,
        "activity_id": 99,
        "activity_name": "Access",
    },
    "process_creation": {
        "class_uid": 1007,
        "category_uid": 1,
        "activity_id": 1,
    },
    "process_tampering": {
        "class_uid": 1007,
        "category_uid": 1,
        "activity_id": 4,
    },
    "process_termination": {
        "class_uid": 1007,
        "category_uid": 1,
        "activity_id": 2,
    },
    # "raw_access_thread": 9,
    "registry_add": {"class_uid": 201001, "category_uid": 1, "activity_id": 1},
    "registry_delete": {"class_uid": 201001, "category_uid": 1, "activity_id": 4},
    "registry_event": {"class_uid": 201001, "category_uid": 1},
    "registry_rename": {"class_uid": 201001, "category_uid": 1, "activity_id": 5},
    "registry_set": {"class_uid": 201001, "category_uid": 1, "activity_id": 3},
    "sysmon_error": {
        "class_uid": 6008,
        "category_uid": 6,
        "activity_id": 1,
    },
    # "sysmon_status": [4, 16],
    # "wmi_event": [19, 20, 21],
}


@Pipeline
def ocsf_pipeline() -> ProcessingPipeline:
    return ProcessingPipeline(
        name="OCSF pipeline",
        allowed_backends=frozenset(),  # Set of identifiers of backends (from the backends mapping) that are allowed to use this processing pipeline. This can be used by frontends like Sigma CLI to warn the user about inappropriate usage.
        priority=20,  # The priority defines the order pipelines are applied. See documentation for common values.
        items=[
            ProcessingItem(
                identifier=f"ocsf_{log_source}_{field}",
                transformation=AddConditionTransformation(
                    {
                        field: value,
                    }
                ),
                rule_conditions=[LogsourceCondition(category=log_source)],
            )
            for log_source, mappeddata in ocsf_generic_logsource_mapping.items()
            for field, value in sorted(mappeddata.items())
        ]
        + [
            ProcessingItem(  # Field mappings for application)
                identifier="ocsf_field_mappings_application",
                transformation=FieldMappingTransformation(
                    {
                        "objectRef.namespace": "unmapped.objectRef.namespace",
                        "objectRef.subresource": "unmapped.objectRef.subresource",
                        "objectRef.resource": "unmapped.objectRef.resource",
                        "EventLog": "metadata.log_name",
                        "InterfaceUuid": "unmapped.InterfaceUuid",
                        "OpNum": "unmapped.OpNum",
                        "apiGroup": "unmapped.apiGroup",
                        "capabilities": "unmapped.capabilities",
                        "verb": "unmapped.verb",
                        "EventID": "metadata.event_code",
                        "logtype": "unmapped.logtype",
                        "hostPath": "unmapped.hostPath",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="application")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for antivirus)
                identifier="ocsf_field_mappings_antivirus",
                transformation=FieldMappingTransformation(
                    {
                        "Filename": "evidences.file.name",
                        "Signature": "finding_info.analytic.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="antivirus")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for create_remote_thread)
                identifier="ocsf_field_mappings_create_remote_thread",
                transformation=FieldMappingTransformation(
                    {
                        "SourceParentImage": "file_result.name",
                        "SourceImage": "file.name",
                        "TargetParentProcessId": "unmapped.TargetParentProcessId",
                        "StartFunction": "unmapped.StartFunction",
                        "StartAddress": "unmapped.StartAddress",
                        "SourceCommandLine": "unmapped.SourceCommandLine",
                        "StartModule": "unmapped.StartModule",
                        "TargetImage": "file_result.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="create_remote_thread")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for create_stream_hash)
                identifier="ocsf_field_mappings_create_stream_hash",
                transformation=FieldMappingTransformation(
                    {
                        "Hash": "file.hashes.value",
                        "Image": "file.name",
                        "Contents": "unmapped.Contents",
                        "TargetFilename": "file.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="create_stream_hash")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for dns)
                identifier="ocsf_field_mappings_dns",
                transformation=FieldMappingTransformation(
                    {
                        "answer": "answer.rdata",
                        "record_type": "query.type",
                        "query": "query.hostname",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="dns")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for dns_query)
                identifier="ocsf_field_mappings_dns_query",
                transformation=FieldMappingTransformation(
                    {
                        "QueryName": "query.hostname",
                        "Image": "query.hostname",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="dns_query")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for driver_load)
                identifier="ocsf_field_mappings_driver_load",
                transformation=FieldMappingTransformation(
                    {
                        "Hashes": "process.file.hashes.value",
                        "ImageLoaded": "process.file.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="driver_load")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for firewall)
                identifier="ocsf_field_mappings_firewall",
                transformation=FieldMappingTransformation(
                    {
                        "action": "unmapped.action",
                        "blocked": "unmapped.blocked",
                        "dst_port": "dst_endpoint.port",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="firewall")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for file_access)
                identifier="ocsf_field_mappings_file_access",
                transformation=FieldMappingTransformation(
                    {
                        "Image": "file.name",
                        "FileName": "file.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="file_access")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for file_change)
                identifier="ocsf_field_mappings_file_change",
                transformation=FieldMappingTransformation(
                    {
                        "CreationUtcTime": "file.created_time",
                        "Image": "file.name",
                        "PreviousCreationUtcTime": "unmapped.PreviousCreationUtcTime",
                        "TargetFilename": "file.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="file_change")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for file_delete)
                identifier="ocsf_field_mappings_file_delete",
                transformation=FieldMappingTransformation(
                    {
                        "User": "actor.user.name",
                        "Image": "file.name",
                        "TargetFilename": "file.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="file_delete")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for file_event)
                identifier="ocsf_field_mappings_file_event",
                transformation=FieldMappingTransformation(
                    {
                        "ParentCommandLine": "process.parent_process.cmd_line",
                        "ParentImage": "file.name",
                        "CommandLine": "process.cmd_line",
                        "Image": "file.name",
                        "TargetFilename": "file.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="file_event")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for file_executable_detected)
                identifier="ocsf_field_mappings_file_executable_detected",
                transformation=FieldMappingTransformation(
                    {
                        "TargetFilename": "file.name",
                    }
                ),
                rule_conditions=[
                    LogsourceCondition(category="file_executable_detected")
                ],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for file_rename)
                identifier="ocsf_field_mappings_file_rename",
                transformation=FieldMappingTransformation(
                    {
                        "SourceFilename": "file.name",
                        "TargetFilename": "file_result.file.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="file_rename")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for image_load)
                identifier="ocsf_field_mappings_image_load",
                transformation=FieldMappingTransformation(
                    {
                        "Company": "Company",
                        "Hashes": "process.file.hashes.value",
                        "SignatureStatus": "SignatureStatus",
                        "Signed": "Signed",
                        "CommandLine": "process.cmd_line",
                        "Description": "Description",
                        "OriginalFileName": "process.file.internal_name",
                        "Image": "process.file.name",
                        "Signature": "Signature",
                        "Product": "Product",
                        "ImageLoaded": "process.file.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="image_load")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for network_connection)
                identifier="ocsf_field_mappings_network_connection",
                transformation=FieldMappingTransformation(
                    {
                        "SourcePort": "src_endpoint.port",
                        "DestinationPort": "dst_endpoint.port",
                        "ParentImage": "ParentImage",
                        "CommandLine": "CommandLine",
                        "SourceHostname": "src_endpoint.hostname",
                        "DestinationHostname": "dst_endpoint.hostname",
                        "SourceIsIpv6": "SourceIsIpv6",
                        "Image": "Image",
                        "DestinationIp": "dst_endpoint.ip",
                        "SourceIp": "src_endpoint.ip",
                        "Initiated": "Initiated",
                        "Protocol": "protocol_name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="network_connection")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for pipe_created)
                identifier="ocsf_field_mappings_pipe_created",
                transformation=FieldMappingTransformation(
                    {
                        "Image": "Image",
                        "PipeName": "PipeName",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="pipe_created")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for process_access)
                identifier="ocsf_field_mappings_process_access",
                transformation=FieldMappingTransformation(
                    {
                        "SourceImage": "parent_process.name",
                        "GrantedAccess": "GrantedAccess",
                        "Provider_Name": "Provider_Name",
                        "CallTrace": "CallTrace",
                        "SourceUser": "SourceUser",
                        "TargetImage": "process.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="process_access")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for process_creation)
                identifier="ocsf_field_mappings_process_creation",
                transformation=FieldMappingTransformation(
                    {
                        "Hashes": "Hashes",
                        "User": "process.user.name",
                        "CommandLine": "process.cmd_line",
                        "ParentCommandLine": "process.parent_process.cmd_line",
                        "Image": "process.name",
                        "Description": "process.file.desc",
                        "LogonId": "process.session.uid",
                        "CurrentDirectory": "process.working_directory",
                        "OriginalFileName": "process.file.internal_name",
                        "Provider_Name": "Provider_Name",
                        "ParentUser": "ParentUser",
                        "FileVersion": "FileVersion",
                        "Company": "Company",
                        "Product": "Product",
                        "ParentImage": "process.parent_process.name",
                        "IntegrityLevel": "IntegrityLevel",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="process_creation")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for process_tampering)
                identifier="ocsf_field_mappings_process_tampering",
                transformation=FieldMappingTransformation(
                    {
                        "Type": "Type",
                        "Image": "process.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="process_tampering")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for process_termination)
                identifier="ocsf_field_mappings_process_termination",
                transformation=FieldMappingTransformation(
                    {
                        "Type": "Type",
                        "Image": "process.name",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="process_termination")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for proxy)
                identifier="ocsf_field_mappings_proxy",
                transformation=FieldMappingTransformation(
                    {
                        "c-useragent": "c-useragent",
                        "dst_ip": "dst_ip",
                        "cs-uri": "cs-uri",
                        "cs-method": "cs-method",
                        "c-uri-extension": "c-uri-extension",
                        "cs-host": "cs-host",
                        "c-uri": "c-uri",
                        "cs-cookie": "cs-cookie",
                        "c-uri-query": "c-uri-query",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="proxy")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for ps_classic_provider_start)
                identifier="ocsf_field_mappings_ps_classic_provider_start",
                transformation=FieldMappingTransformation(
                    {
                        "Data": "Data",
                    }
                ),
                rule_conditions=[
                    LogsourceCondition(category="ps_classic_provider_start")
                ],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for ps_classic_start)
                identifier="ocsf_field_mappings_ps_classic_start",
                transformation=FieldMappingTransformation(
                    {
                        "Data": "Data",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="ps_classic_start")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for ps_module)
                identifier="ocsf_field_mappings_ps_module",
                transformation=FieldMappingTransformation(
                    {
                        "ContextInfo": "ContextInfo",
                        "Payload": "Payload",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="ps_module")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for ps_script)
                identifier="ocsf_field_mappings_ps_script",
                transformation=FieldMappingTransformation(
                    {
                        "ScriptBlockText": "ScriptBlockText",
                        "Path": "Path",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="ps_script")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for raw_access_thread)
                identifier="ocsf_field_mappings_raw_access_thread",
                transformation=FieldMappingTransformation(
                    {
                        "Device": "Device",
                        "Image": "Image",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="raw_access_thread")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for registry_add)
                identifier="ocsf_field_mappings_registry_add",
                transformation=FieldMappingTransformation(
                    {
                        "EventType": "EventType",
                        "TargetObject": "reg_key.path",
                        "Image": "reg_key.path",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="registry_add")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for registry_delete)
                identifier="ocsf_field_mappings_registry_delete",
                transformation=FieldMappingTransformation(
                    {
                        "EventType": "EventType",
                        "TargetObject": "reg_key.path",
                        "Image": "reg_key.path",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="registry_delete")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for registry_event)
                identifier="ocsf_field_mappings_registry_event",
                transformation=FieldMappingTransformation(
                    {
                        "NewName": "NewName",
                        "TargetObject": "reg_key.path",
                        "Image": "reg_key.path",
                        "EventType": "EventType",
                        "EventID": "metadata.event_code",
                        "Details": "Details",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="registry_event")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for registry_rename)
                identifier="ocsf_field_mappings_registry_rename",
                transformation=FieldMappingTransformation(
                    {
                        "EventType": "EventType",
                        "TargetObject": "reg_key.path",
                        "Image": "reg_key.path",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="registry_rename")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for registry_set)
                identifier="ocsf_field_mappings_registry_set",
                transformation=FieldMappingTransformation(
                    {
                        "User": "User",
                        "TargetObject": "reg_key.path",
                        "Image": "reg_key.path",
                        "EventType": "EventType",
                        "Details": "Details",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="registry_set")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for sysmon_error)
                identifier="ocsf_field_mappings_sysmon_error",
                transformation=FieldMappingTransformation(
                    {
                        "Description": "message",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="sysmon_error")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for sysmon_status)
                identifier="ocsf_field_mappings_sysmon_status",
                transformation=FieldMappingTransformation(
                    {
                        "State": "State",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="sysmon_status")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for webserver)
                identifier="ocsf_field_mappings_webserver",
                transformation=FieldMappingTransformation(
                    {
                        "cs-uri-query": "cs-uri-query",
                        "cs-method": "cs-method",
                        "sc-status": "sc-status",
                        "cs-user-agent": "cs-user-agent",
                        "cs-referer": "cs-referer",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="webserver")],
            )
        ]
        + [
            ProcessingItem(  # Field mappings for wmi_event)
                identifier="ocsf_field_mappings_wmi_event",
                transformation=FieldMappingTransformation(
                    {
                        "EventID": "metadata.event_code",
                        "Destination": "Destination",
                    }
                ),
                rule_conditions=[LogsourceCondition(category="wmi_event")],
            )
        ],
    )
