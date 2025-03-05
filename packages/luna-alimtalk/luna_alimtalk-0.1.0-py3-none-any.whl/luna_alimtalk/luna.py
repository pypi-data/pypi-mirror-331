import httpx
from httpx import Response
from typing import List, Dict, Union, Optional
from dataclasses import dataclass


endpoint = "https://jupiter.lunasoft.co.kr/api/AlimTalk/message/send"


@dataclass
class Message:
    no: str
    tel_num: str
    msg_content: str
    use_sms: str
    btn_url: Optional[List[dict]] = None

    def to_dict(self) -> Dict:
        data = {
            "no": self.no,
            "tel_num": self.tel_num,
            "msg_content": self.msg_content,
            "use_sms": self.use_sms
        }
        if self.btn_url:
            data["btn_url"] = [btn for btn in self.btn_url]
        return data


def get_message_with_params(
        message: str,
        params: Optional[Dict[str, str]] = None,
        options=None
) -> str:
    if options is None:
        options = {"opening": "{", "closing": "}"}

    if not params:
        return message

    for key, text in params.items():
        pattern = f"{options['opening']}{key}{options['closing']}"
        message = message.replace(pattern, text)

    return message


class Luna:
    def __init__(self, userid: str, api_key: str):
        self.userid = userid
        self.api_key = api_key

    async def send_messages(self, template_id: str, messages: List[Message]) -> Response:
        payload = {
            "userid": self.userid,
            "api_key": self.api_key,
            "template_id": template_id,
            "messages": [msg.to_dict() for msg in messages]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json; charset=utf-8"}
                )
                return response
            except httpx.RequestError as err:
                raise Exception(f"API 요청 실패: {err}")

    async def send_with_phone(
            self,
            contacts: Union[str, List[str]],
            template_id: str,
            message: str,
            params: Optional[Dict[str, str]] = None,
            urls: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
            use_sms: bool = False
    ) -> Response:
        contacts_list = contacts if isinstance(contacts, list) else [contacts]
        urls = urls if urls is not None else None
        if not urls:
            btn_urls = None
        else:
            btn_urls = urls if isinstance(urls, list) else [urls]

        messages = [
            Message(
                no=str(i),
                tel_num=tel_num,
                msg_content=get_message_with_params(message, params),
                use_sms="1" if use_sms else "0",
                btn_url=btn_urls
            ) for i, tel_num in enumerate(contacts_list)
        ]

        return await self.send_messages(template_id, messages)