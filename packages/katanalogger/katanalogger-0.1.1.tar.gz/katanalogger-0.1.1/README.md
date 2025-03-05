# KatanaLogger
Fast logger with lots of settings and cool output🥷
<br/>
Logger on python for my project, easy usage🌀



### Preview with emoji 🪄
![Code_td6mLDBKdu](https://github.com/user-attachments/assets/fae3e5e2-e5c9-4280-8b05-c11fae864f04)

### Preview no emoji😶‍

![Code_MrLOVw4rCU](https://github.com/user-attachments/assets/4595b7c7-22dc-4fe8-9971-ad16fae2cc15)


## Just Usage
```python
logger = Logger()
await logger.debug("CSRF token not found!")
await logger.log("App is running")
await logger.die("Service error 55 line")
```
![изображение](https://github.com/user-attachments/assets/8ad5f279-57c8-4814-b5cd-c77b8f693b49)


## Traceback Parsing
```python
try:
    1 / 0
except Exception as e:
    await logger.log_traceback(e)
```
![изображение](https://github.com/user-attachments/assets/b58b1f4b-20b2-4d0d-b50e-9561af401001)



### Tools

### Wait progress example🆙
![Code_jh4ej0Nkdu](https://github.com/user-attachments/assets/9948bca7-15eb-4a68-8e3c-3ef30fbbe368)

![изображение](https://github.com/user-attachments/assets/6bebc04b-41f1-4b92-8548-43784183d326)

```python
@Decorators.ms
def test():
    for i in range(1, 33):
        print(i)


#OR ASYNC

@Decorators.ms
async def test():
    for i in range(1, 33):
        print(i)
```
![Code_kJVo9ak8Hp](https://github.com/user-attachments/assets/d26c38a4-665f-44ca-ac66-1d4b32cd9233)



