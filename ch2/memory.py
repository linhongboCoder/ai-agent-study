import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

class AgentMemory:
    def __init__(self, max_short_item:int=10):
        self.max_short_item = max_short_item
        self.working = {}
        self.long_term = []
        self.short_term = []
        self.summary = ""

    def add_conversation(self, user_msg:str, assistant_msg:str):
        self.short_term.append((user_msg, assistant_msg))
        if len(self.short_term) > self.max_short_item:
            self.compress()

    def compress(self):
        old_pair = self.short_term.pop(0)
        combined = f"[用户]: {old_pair[0]}\n[助手]: {old_pair[1]}"
        self.long_term.append(combined)
        if not self.summary:
            self.summary = f"早期对话摘要：\n{combined}"
        else:
            self.summary += f"\n{combined}"
            
    def set_working(self, key: str, value: str):
        self.working[key] = value

    def get_working(self,key:str)->str:
        return self.working.get(key, "")
    
    def get_context_for_llm(self)->str:
        parts = []

        if self.summary:
            parts.append(f"## 历史摘要\n{self.summary}\n")

        if self.working:
            wk_items = "\n".join(
                f"  {k}: {v}" for k, v in self.working.items()
            )
            parts.append(f"## 当前任务状态\n{wk_items}\n")

        if self.short_term:
            recent = "\n".join(
                f"用户: {u}\n助手: {a}"
                for u, a in self.short_term[-5:]
            )
            parts.append(f"## 最近对话\n{recent}")

        return "\n".join(parts)        


