# Anura SDK for Python

The **Anura SDK for Python** makes it easy for developers to access Anura Direct within their Python code, and begin analyzing their traffic. You can get started in minutes by installing the SDK from PyPI or our source code.

## Getting Started
1. **Have an open active account with Anura**. You can see more about Anura's offerings [here.](https://www.anura.io/product#plans-pricing)
2. **Minimum Requirements** - To use the SDK, you will need **Python >=3.10**.
3. **Install the SDK** - Using **pip** is the easiest and recommended way to install it. You can install it with the following command:
```sh
pip install anura
```
Or, install from source by using one of the following examples according to your operating system:

Linux/Mac:
```sh
git clone https://github.com/anuraio/anura-sdk-python.git
cd anura-sdk-python
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

Windows:
```sh
git clone https://github.com/anuraio/anura-sdk-python.git
cd anura-sdk-python
py -m pip install -r requirements.txt
py -m pip install -e .
```

4. View our [**Quick Examples**](#quick-examples) to immediately begin using the SDK!

## Quick Examples
### Create the Anura Direct Client
```python
from anura.direct.client import AnuraDirect

direct = AnuraDirect('your-instance-id-goes-here')
```
### Create additional data for Anura Direct
For sending additional data, you can use a `dict`. We'll use this `additional_data` when we fetch a result:
```python
additional_data = {}
index = 1

# adding element
additional_data[index] = 'your-data-value'

# updating an element (adding the element again, but with a new value)
additional_data[index] = 'your-new-data-value'

# removing an element
del additional_data[index]
```

### Get a result from Anura Direct
```python
try:
    result = direct.get_result(
        ip_address='visitors-ip-address',   # required
        user_agent='visitors-user-agent',   # optional
        app='visitors-app-package-id',      # optional
        device='visitors-device-id',        # optional
        source='your-source-value',         # optional
        campaign='your-campaign-value',     # optional
        additional_data=additional_data     # optional

    )

    if (result.is_suspect()):
        # Perform some logic only for suspect visitors
        print('Visitor is suspect.')

    if (result.is_non_suspect()):
        # Perform some logic only for non-suspect visitors
        print('Visitor is non-suspect.')

    if (result.is_mobile()):
        # Perform some logic only for visitors from mobile devices
        print('Visitor is using a mobile device.')

    is_web_crawler = (result.rule_sets is not None and "WC" in result.rule_sets)
    if (is_web_crawler):
        # Perform some logic only for web crawlers
        print('Visitor is a web crawler.')

    print('result: ' + str(result))

except Exception as e:
    print(e)
```

### Get a result from Anura Direct asynchronously
```python
import asyncio
import aiohttp

async def main():
    direct = AnuraDirect('your-instance-id')

    async with aiohttp.ClientSession() as session:
        try:
            result = await direct.get_result_async(
                session=session,                    # required
                ip_address='visitors-ip-address',   # required
                user_agent='visitors-user-agent',   # optional
                app='visitors-app-package-id',      # optional
                device='visitors-device-id',        # optional
                source='your-source-value',         # optional
                campaign='your-campaign-value',     # optional
                additional_data=additional_data     # optional
            )

            if (result.is_suspect()):
                # Perform some logic only for suspect visitors
                print('Visitor is suspect.')

            if (result.is_non_suspect()):
                # Perform some logic only for non-suspect visitors
                print('Visitor is non-suspect.')

            if (result.is_mobile()):
                # Perform some logic only for visitors from mobile devices
                print('Visitor is using a mobile device.')

            is_web_crawler = (result.rule_sets is not None and "WC" in result.rule_sets)
            if (is_web_crawler):
                # Perform some logic only for web crawlers
                print('Visitor is a web crawler.')

            print('result: ' + str(result))
        except Exception as e:
            print(e)

asyncio.run(main())
```


## API Reference
### AnuraDirect
Can get results from Anura Direct. These results are fetched using Direct's `/direct.json` API endpoint.

#### Methods
**`get_result() -> DirectResult`**
- Gets a result synchronously from Anura Direct. Raises an exception if an error occurs throughout the result fetching process.
- Exceptions thrown:
    - `AnuraException`: if a 4XX, 5XX, or any unknown response is returned from Anura Direct

Parameters:
| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| `ip_address` | `str` | The IP address of your visitor. Both IPv4 & IPv6 addresses are supported. | Yes |
| `user_agent` | `str` | The user agent string of your visitor | |
| `app` | `str` | The application package identifier of your visitor (when available.) | |
| `device` | `str` | The device identifier of your visitor (when available.) | |
| `source` | `str` | A variable, declared by you, to identify "source" traffic within Anura's dashboard interface. | |
| `campaign` | `str` | A subset variable of "source", declared by you, to identify "campaign" traffic within Anura's dashboard interface. | |
| `additional_data` | `dict` | Additional Data gives you the ability to pass in select points of data with your direct requests, essentially turning Anura into "your database for transactional data." | |

**`get_result_async() -> Awaitable[DirectResult]`**
- Gets a result asynchronously from Anura Direct. Raises an exception if an error occurs throughout the result fetching process.
- Exceptions thrown:
    - `AnuraException`: if a 4XX, 5XX, or any unknown response is returned from Anura Direct

Parameters:
| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| `session` | `aiohttp.ClientSession` | The aiohttp client session object | Yes |
| `ip_address` | `str` | The IP address of your visitor. Both IPv4 & IPv6 addresses are supported. | Yes |
| `user_agent` | `str` | The user agent string of your visitor | |
| `app` | `str` | The application package identifier of your visitor (when available.) | |
| `device` | `str` | The device identifier of your visitor (when available.) | |
| `source` | `str` | A variable, declared by you, to identify "source" traffic within Anura's dashboard interface. | |
| `campaign` | `str` | A subset variable of "source", declared by you, to identify "campaign" traffic within Anura's dashboard interface. | |
| `additional_data` | `dict` | Additional Data gives you the ability to pass in select points of data with your direct requests, essentially turning Anura into "your database for transactional data." | |

**`@property instance(self) -> str`**
- Returns the instance you have set within the `AnuraDirect` client.

**`@instance.setter instance(self, instance: str) -> None`**
- Sets the Instance ID of the `AnuraDirect` client to the `instance` value passed.

**`@property use_https(self) -> bool`**
- Returns whether or you're currently using **HTTPS** when calling the Anura Direct API. If false, you are using **HTTP** instead.

**`@use_https.setter use_https(self, use_https: bool) -> None`**
- Sets whether to use **HTTPS** or **HTTP** according to the `use_https` value passed.

### DirectResult
The result upon a successful call to `get_result()` or `get_result_async()` from the `AnuraDirect` client. It contains not only the result from Anura Direct, but some other methods to help you use the result as well.

#### Methods
**`is_suspect() -> bool`**
- Returns whether or not the visitor has been determined to be **suspect**.

**`is_non_suspect() -> bool`**
- Returns whether or not the visitor has been determined to be **non-suspect**.

**`is_mobile() -> bool`**
- Returns whether or not the visitor has been determined to be on a mobile device.

#### Properties
**`result: str`**
- Besides using the `is_suspect()` or `is_non_suspect()` methods, you are also able to directly access the result value.

**`mobile: int | None`**
- Besides using the `is_mobile()` method, you are also able to directly access the mobile value.

**`rule_sets: list[str] | None`**
- If you have **return rule sets** enabled, you will be able to see which specific rules were violated upon a **suspect** result. This value will be `None` if the visitor is **non-suspect**, or if you do not have **return rule sets** enabled.
- You can talk to [support](mailto:support@anura.io) about enabling or disabling the **return rule sets** feature.

**`invalid_traffic_type: str | None`**
- If you have **invalid traffic type** enabled, you will be able to access which type of invalid traffic occurred upon a **suspect** result.
- You can talk to [support](mailto:support@anura.io) about enabling or disabling the **return invalid traffic type** feature.
