#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

import openai
import os
import random
import re
import json

# LLM 大模型任务类
class LLM_TASK():
    def __init__(self, api_key, base_url="", 
            proxy=None, prompt_template='', model="", 
            use_system_prompt=0, result_replace_dict={}):

        # 提示词模板
        prompt_template = re.sub(r"\n +", r"\n", prompt_template)
        self.prompt_template = prompt_template

        # api key
        self.api_key = api_key
        # 模型名称
        self.model = model
        self.use_system_prompt = use_system_prompt  # 是否使用系统提示词

        # token使用时统计
        self.total_tokens = 0
        self.usages = []

        # 调试
        self.debug = 0

        # 自定义结果替换：字典
        self.result_replace_dict = result_replace_dict
        
        self.base_url = base_url
        if proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    @staticmethod
    def clear_text(txt, key, pos=0) -> str:
        # 用于清理格式
        if pos==0: # 开头
            if txt.startswith(key): txt = txt[len(key):]
        else: # 结尾
            if txt.endswith(key): txt = txt[:-len(key)]
        return txt

    @staticmethod
    def haschar(text: str, avoid: str) -> bool:
        ''' 判断text中是否包含avoid中的任意一个字符；
        '''
        text_chars = set(text)
        void_chars = set(avoid)
        # 利用集合的交集操作，如果text的字符集合与void的字符集合有交集，则说明text包含void中的字符
        return bool(text and avoid and text_chars.intersection(void_chars))

    @staticmethod
    def replace_dict (txt, dictKey, isreg=0):
        '''按字典进行批量替换
        isreg: 是否启用正则
        '''
        tmptxt = txt
        for k, v in dictKey.items():
            if isreg:
                tmptxt = re.sub(k, v, tmptxt)
            else:
                tmptxt = tmptxt.replace(k, v)
        return tmptxt

    def txt2json(self, text):
        ''' 把文本解析成JSON，用于处理大模型输出的各类异常格式；
        '''
        try:
            # 增加：自定义替换； 2024/5/8
            if self.result_replace_dict:
                text = self.replace_dict (text, self.result_replace_dict)

            # 去掉各行的空格及换行
            text = ''.join([x.strip() for x in text.splitlines()])

            # 格式化处理
            text = self.clear_text(text, '```json', 0)
            text = self.clear_text(text, '```', 1)
            # 单引号换成双引号
            text = text.replace("'", '"')
            # 标准列表
            npat = r"^\[ *(\"[\w\- _\\u4E00-\\u9FA5]+\"( *, *)?)+ *\]$"
            nret = re.match(npat, text)
            if nret:
                jdat = json.loads(text)
                return jdat

            # 如果不含括号引号等: "{}[]"，则判断为纯文本，转换成列表
            ## 处理[abc, "其它"] 这样的格式

            # 注意：处理："[tec]"这样的格式 2024/11/1
            # pat = r"^\[([\w, \-_]+)\]$"
            pat = r"^\[([\w,\-'\" _\\u4E00-\\u9FA5]+)\]$"
            mret = re.match(pat, text)
            if mret:
                if self.debug:
                    print(f'found format:{text}')
                tmp = mret[0][1:-1].replace(" ", "")
                items = [x.replace("\"", "") for x in tmp.split(",")]
                text = '["' + '","'.join(items) + '"]'
                if self.debug:
                    print(f'fixed format:{text}')
            elif not self.haschar(text,  "{}[]\"'"):
                text = f"[\"{text}\"]"

            # 如果以引号开头和结尾，则认为是纯文本，将其头尾加上[]转化为列表
            elif (text.startswith('"') and text.endswith('"')) or \
                (text.startswith("'") and text.endswith("'")):
                text = f"[{text}]"
            if self.debug:
                print(f'debug: {type(text)}, {text}\n')

            # 转为JSON格式
            jdat = json.loads(text)
            return jdat
        except Exception as e:
            print("text: ", text)
            print('error on txt2json:', e)
            # 格式不正确时返回原文本
            return text

    def call_with_messages(self, prompt, history=[],
                system_prompt='', token_count=None):
        ''' OpenAI接口调用LLM
        '''
        messages = []
        if system_prompt != '':
            messages.append({'role': 'system', 'content': system_prompt})
        else:
            messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]

        # 添加历史记录
        if history:
            messages.extend(history)
        # 添加用户问题
        messages.append({'role': 'user', 'content': prompt})

        # 调用LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                seed=random.randint(0, 1000),
                temperature=0.1,        # 0.8
            )
            if response:
                ret = response.choices[0].message.content

                # 记录token使用量
                if not token_count is None:
                    usage = dict(response.usage)
                    token_count.add_token(usage)
            else:
                print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                    response.request_id, response.status_code,
                    response.code, response.message
                ))
                # 出错返回原始文本
                ret = ''
            return ret
        except Exception as e:
            print(e)
            return ""

    def add_token(self, usage:dict):
        ''' 添加token使用量
        '''
        self.usages.append(dict(usage))
        total_tokens = usage.get('total_tokens', 0)
        self.total_tokens += total_tokens

    def predict(self, parm:dict):
        ''' 执行任务
        '''

        # 生成提示词
        if self.use_system_prompt:
            query = ''.join(parm.values())
            ret = self.call_with_messages(query,
                        system_prompt=self.prompt_template,
                        token_count=self)
        else:
            prompt = self.replace_dict(self.prompt_template, parm)
            ret = self.call_with_messages(prompt, token_count=self)

        if self.debug:
            print('model ret:', ret)

        # 转换解析JSON
        jdat = self.txt2json(ret)
        return jdat

def test_llm_task():
    cfg = [
        "http://192.168.15.111:3000/v1",
        "sk-GQtwF5ag8p6m8wWf1232B8D5E17f4455A5C14e7a2d393aEe",
        "deepseek-chat"
    ]
    base_url, api_key, model = cfg

    prompt_template = """
    # 请根据用户的关键词生成一首五言绝句
    # 关键词：
    {keyword}
    """

    llm = LLM_TASK(api_key, base_url=base_url, model=model, prompt_template=prompt_template)
    parm = {"{keyword}":"春天 浓雾 动荡的国际形势"}
    result = llm.predict(parm)
    print(result)

if __name__ == '__main__':
    pass
    test_llm_task()
    # import fire
    # fire.Fire()

