from typing import Literal
from dataclasses import dataclass
from config.config import get_config

@dataclass
class GenerationParams:
    length: Literal['short', 'medium', 'long']
    strength: Literal['subtle', 'balanced', 'strong']

def build_prompt(tov: str, input_text: str, instructions: str, params: GenerationParams) -> str:
    cfg = get_config()
    max_tokens_map = {
        'short': cfg.max_tokens_short,
        'medium': cfg.max_tokens_medium,
        'long': cfg.max_tokens_long,
    }
    style_hint_map = {
        'subtle': 'Make minimal changes while aligning with tone of voice.',
        'balanced': 'Balance clarity and tone; improve structure and persuasiveness.',
        'strong': 'Boldly rewrite to maximize impact, while preserving core meaning.',
    }
    max_tokens = max_tokens_map[params.length]
    style_hint = style_hint_map[params.strength]
    instructions_block = 'Specific instructions: {}'.format(instructions.strip()) if instructions.strip() else ''
    template = (
        'You are a senior marketing copywriter. Follow the Tone of Voice (TOV) and constraints strictly.\n'
        'Tone of Voice (TOV):\n{tov}\n\n'
        'Task: Rewrite or generate the marketing text. Preserve factual accuracy.\n'
        'Constraints: Output length target: {length}. You may use up to {max_tokens} tokens. {style_hint}\n'
        'Provide only the rewritten text; do not include explanations.\n\n'
        'Initial Text:\n{input_text}\n\n'
        'Desired Output:\n{instructions_block}\n'
    )
    return template.format(tov=tov.strip(), length=params.length, max_tokens=max_tokens, style_hint=style_hint, input_text=input_text.strip(), instructions_block=instructions_block)

class LLMEngine:
    def __init__(self):
        self.cfg = get_config()
        self._init_openai()

    def _init_openai(self) -> None:
        self._openai = None
        if self.cfg.openai_api_key:
            try:
                from openai import OpenAI  # type: ignore
                self._openai = OpenAI(api_key=self.cfg.openai_api_key)
            except Exception:
                self._openai = None

    def generate(self, prompt: str, params: GenerationParams) -> str:
        if not self._openai:
            return '[Missing or invalid OPENAI_API_KEY] Cannot generate output.'
        return self._generate_openai(prompt, params)

    def _map_temperature(self, strength: str) -> float:
        return {
            'subtle': self.cfg.temperature_subtle,
            'balanced': self.cfg.temperature_balanced,
            'strong': self.cfg.temperature_strong,
        }[strength]

    def _map_max_tokens(self, length: str) -> int:
        return {
            'short': self.cfg.max_tokens_short,
            'medium': self.cfg.max_tokens_medium,
            'long': self.cfg.max_tokens_long,
        }[length]

    def _generate_openai(self, prompt: str, params: GenerationParams) -> str:
        temperature = self._map_temperature(params.strength)
        max_tokens = self._map_max_tokens(params.length)
        try:
            resp = self._openai.chat.completions.create(
                model=self.cfg.openai_model,
                messages=[{'role': 'system', 'content': 'You rewrite marketing copy.'}, {'role': 'user', 'content': prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return (resp.choices[0].message.content or '').strip()
        except Exception as e:
            return '[Generation error: {}]'.format(e)

