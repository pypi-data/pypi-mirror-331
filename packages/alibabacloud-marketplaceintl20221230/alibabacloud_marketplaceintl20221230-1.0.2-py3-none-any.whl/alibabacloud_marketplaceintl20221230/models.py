# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from Tea.model import TeaModel
from typing import List, Dict


class PushMeteringDataRequestMeteringData(TeaModel):
    def __init__(
        self,
        end_time: int = None,
        instance_id: str = None,
        metering_assist: str = None,
        metering_entity: str = None,
        start_time: int = None,
    ):
        self.end_time = end_time
        self.instance_id = instance_id
        self.metering_assist = metering_assist
        self.metering_entity = metering_entity
        self.start_time = start_time

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.end_time is not None:
            result['EndTime'] = self.end_time
        if self.instance_id is not None:
            result['InstanceId'] = self.instance_id
        if self.metering_assist is not None:
            result['MeteringAssist'] = self.metering_assist
        if self.metering_entity is not None:
            result['MeteringEntity'] = self.metering_entity
        if self.start_time is not None:
            result['StartTime'] = self.start_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('EndTime') is not None:
            self.end_time = m.get('EndTime')
        if m.get('InstanceId') is not None:
            self.instance_id = m.get('InstanceId')
        if m.get('MeteringAssist') is not None:
            self.metering_assist = m.get('MeteringAssist')
        if m.get('MeteringEntity') is not None:
            self.metering_entity = m.get('MeteringEntity')
        if m.get('StartTime') is not None:
            self.start_time = m.get('StartTime')
        return self


class PushMeteringDataRequest(TeaModel):
    def __init__(
        self,
        gmt_create: str = None,
        metering_data: List[PushMeteringDataRequestMeteringData] = None,
    ):
        self.gmt_create = gmt_create
        self.metering_data = metering_data

    def validate(self):
        if self.metering_data:
            for k in self.metering_data:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.gmt_create is not None:
            result['GmtCreate'] = self.gmt_create
        result['MeteringData'] = []
        if self.metering_data is not None:
            for k in self.metering_data:
                result['MeteringData'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('GmtCreate') is not None:
            self.gmt_create = m.get('GmtCreate')
        self.metering_data = []
        if m.get('MeteringData') is not None:
            for k in m.get('MeteringData'):
                temp_model = PushMeteringDataRequestMeteringData()
                self.metering_data.append(temp_model.from_map(k))
        return self


class PushMeteringDataResponseBody(TeaModel):
    def __init__(
        self,
        code: str = None,
        dynamic_message: str = None,
        force_fatal: bool = None,
        message: str = None,
        request_id: str = None,
        result: bool = None,
        success: bool = None,
    ):
        self.code = code
        self.dynamic_message = dynamic_message
        self.force_fatal = force_fatal
        self.message = message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['Code'] = self.code
        if self.dynamic_message is not None:
            result['DynamicMessage'] = self.dynamic_message
        if self.force_fatal is not None:
            result['ForceFatal'] = self.force_fatal
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.result is not None:
            result['Result'] = self.result
        if self.success is not None:
            result['Success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Code') is not None:
            self.code = m.get('Code')
        if m.get('DynamicMessage') is not None:
            self.dynamic_message = m.get('DynamicMessage')
        if m.get('ForceFatal') is not None:
            self.force_fatal = m.get('ForceFatal')
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('Result') is not None:
            self.result = m.get('Result')
        if m.get('Success') is not None:
            self.success = m.get('Success')
        return self


class PushMeteringDataResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: PushMeteringDataResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = PushMeteringDataResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


