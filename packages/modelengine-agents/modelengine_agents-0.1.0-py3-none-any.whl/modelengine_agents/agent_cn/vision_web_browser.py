import argparse
from io import BytesIO
from time import sleep

import helium
from dotenv import load_dotenv
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from smolagents import CodeAgent, DuckDuckGoSearchTool, tool
from smolagents.agents import ActionStep
from smolagents.cli import load_model


github_request = """
我想了解要让一个仓库进入 github.com/trending 需要付出多少努力。
你能导航到排名第一的热门仓库的作者主页，告诉我他们在过去一年中的总提交次数吗？
"""  # The agent is able to achieve this request only when powered by GPT-4o or Claude-3.5-sonnet.

search_request = """
请导航到 https://en.wikipedia.org/wiki/Chicago 并找到一个包含"1992"且提到建筑事故的句子。
"""


def parse_arguments():
    parser = argparse.ArgumentParser(description="使用指定模型运行网页浏览器自动化脚本。")
    parser.add_argument(
        "prompt",
        type=str,
        nargs="?",  # Makes it optional
        default=search_request,
        help="要让代理执行的提示词",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="LiteLLMModel",
        help="要使用的模型类型（例如：OpenAIServerModel, LiteLLMModel, TransformersModel, HfApiModel）",
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default="gpt-4o",
        help="指定模型类型要使用的模型ID",
    )
    return parser.parse_args()


def save_screenshot(memory_step: ActionStep, agent: CodeAgent) -> None:
    sleep(1.0)  # Let JavaScript animations happen before taking the screenshot
    driver = helium.get_driver()
    current_step = memory_step.step_number
    if driver is not None:
        for previous_memory_step in agent.memory.steps:  # Remove previous screenshots from logs for lean processing
            if isinstance(previous_memory_step, ActionStep) and previous_memory_step.step_number <= current_step - 2:
                previous_memory_step.observations_images = None
        png_bytes = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(png_bytes))
        print(f"已捕获浏览器截图：{image.size} 像素")
        memory_step.observations_images = [image.copy()]  # Create a copy to ensure it persists, important!

    # Update observations with current URL
    url_info = f"当前URL：{driver.current_url}"
    memory_step.observations = (
        url_info if memory_step.observations is None else memory_step.observations + "\n" + url_info
    )
    return


@tool
def search_item_ctrl_f(text: str, nth_result: int = 1) -> str:
    """
    通过Ctrl + F在当前页面搜索文本并跳转到第n个匹配项。
    参数：
        text: 要搜索的文本
        nth_result: 要跳转到第几个匹配项（默认：1）
    """
    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
    if nth_result > len(elements):
        raise Exception(f"未找到第{nth_result}个匹配项（仅找到{len(elements)}个匹配项）")
    result = f"找到{len(elements)}个匹配项'{text}'。"
    elem = elements[nth_result - 1]
    driver.execute_script("arguments[0].scrollIntoView(true);", elem)
    result += f"已聚焦到第{nth_result}个元素（共{len(elements)}个）"
    return result


@tool
def go_back() -> None:
    """返回上一页。"""
    driver.back()


@tool
def close_popups() -> str:
    """
    关闭页面上任何可见的模态框或弹窗。使用此工具关闭弹出窗口！这对cookie同意横幅不起作用。
    """
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()


def initialize_driver():
    """Initialize the Selenium WebDriver."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument("--window-size=1000,1350")
    chrome_options.add_argument("--disable-pdf-viewer")
    chrome_options.add_argument("--window-position=0,0")
    return helium.start_chrome(headless=False, options=chrome_options)


def initialize_agent(model):
    """Initialize the CodeAgent with the specified model."""
    return CodeAgent(
        tools=[DuckDuckGoSearchTool(), go_back, close_popups, search_item_ctrl_f],
        model=model,
        additional_authorized_imports=["helium"],
        step_callbacks=[save_screenshot],
        max_steps=20,
        verbosity_level=2,
    )


helium_instructions = """
当你想获取谷歌搜索结果时，使用你的web_search工具。
然后你可以使用helium来访问网站。不要使用helium进行谷歌搜索，只用它来导航网站！
不用担心helium驱动程序，它已经被管理好了。
我们已经运行了"from helium import *"
然后你就可以访问页面了！
代码：
```py
go_to('github.com/trending')
```<end_code>

你可以通过输入元素上显示的文本直接点击可点击的元素。
代码：
```py
click("热门产品")
```<end_code>

如果是链接：
代码：
```py
click(Link("热门产品"))
```<end_code>

如果你尝试与某个元素交互但找不到它，你会收到LookupError。
通常在每次点击按钮后停止操作，查看你的截图中发生了什么。
永远不要尝试在页面上登录。

要上下滚动，使用scroll_down或scroll_up，参数是要滚动的像素数。
代码：
```py
scroll_down(num_pixels=1200) # 这将向下滚动一个视口
```<end_code>

当你遇到带有关闭图标的弹窗时，不要尝试通过查找其元素或定位'X'元素来点击关闭图标（这通常会失败）。
只需使用你的内置工具`close_popups`来关闭它们：
代码：
```py
close_popups()
```<end_code>

你可以使用.exists()来检查元素是否存在。例如：
代码：
```py
if Text('接受cookies？').exists():
    click('我接受')
```<end_code>

分几个步骤进行，而不是试图一次性解决任务。
最后，只有当你有了答案时，才返回你的最终答案。
代码：
```py
final_answer("在此输入你的答案")
```<end_code>

如果页面似乎卡在加载状态，你可能需要等待，例如`import time`并运行`time.sleep(5.0)`。但不要过度使用这个！
要列出页面上的元素，不要尝试基于代码的元素搜索，如'contributors = find_all(S("ol > li"))'：只需查看你最新的截图并用视觉方式阅读，或使用你的工具search_item_ctrl_f。
当然，你可以像用户一样操作按钮进行导航。
在你写的每个代码块之后，你都会自动获得浏览器的最新截图和当前浏览器URL。
但要注意，截图只会在整个操作结束时拍摄，它不会看到中间状态。
不要关闭浏览器。
当屏幕上有模态框或cookie横幅时，你应该先把它们清除掉，然后才能点击其他任何东西。
"""


def main():
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    args = parse_arguments()

    # Initialize the model based on the provided arguments
    model = load_model(args.model_type, args.model_id)

    global driver
    driver = initialize_driver()
    agent = initialize_agent(model)

    # Run the agent with the provided prompt
    agent.python_executor("from helium import *", agent.state)
    agent.run(args.prompt + helium_instructions)


if __name__ == "__main__":
    main()
