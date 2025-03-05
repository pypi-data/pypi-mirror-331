# luna-alimtalk
루나소프트 알림톡 API 패키지

- 샘플 코드
```python
import asyncio

from luna_alimtalk import Luna


async def main():
    luna = Luna(userid='유저 아이디', api_key='API 키')
    response = await luna.send_with_phone(
        contacts='010xxxxxxxx',
        template_id='템플릿 아이디',
        message='{name}님의 회원가입 정보 안내드립니다.\n\n{shop_name} ID : {user_id}\n\n{shop_name} {url}\n고객센터 {tel}',
        params={
                'name': '홍길동',
                'shop_name': '테스트',
                'user_id': 'hong44444',
                'url': 'https://test.co.kr',
                'tel': '010xxxxxxxx',
        },
        urls={
            'url_pc': 'https://test.co.kr',
            'url_mobile': 'https://test.co.kr',
        }
    )
    print(response.status_code)
    print(response.json())


if __name__ == '__main__':
    asyncio.run(main())
```