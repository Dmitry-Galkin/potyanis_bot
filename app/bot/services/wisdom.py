import random

from openai import AsyncOpenAI

from app.config import Config

# (Описание категории, вес): чем больше вес — тем чаще выпадает.
CATEGORIES = [
    (
        "история и происхождение асаны: "
        "что означает ее название на санскрите, откуда она пошла",
        3,
    ),
    (
        "любопытный исторический факт о йоге, ее школах или традициях",
        3,
    ),
    (
        "значение санскритского термина из йоги и как он раскрывает суть практики",
        2,
    ),
    (
        "история жизни известного йогина или учителя и чем он важен",
        2,
    ),
    (
        "неожиданный факт о дыхании, анатомии или устройстве практики",
        2,
    ),
    (
        "история йоги в России: как она появилась и развивалась, известные "
        "отечественные практики и исследователи, интересные факты",
        2,
    ),
    (
        "короткая философская мысль о пути йоги",
        1,
    ),
]
# Системный промпт.
SYSTEM_PROMPT = (
    "Ты — знающий и увлеченный преподаватель йоги, "
    "который ведет образовательный канал. "
    "Пишешь живо, по-русски, без пафоса и заезженных цитат."
)


def _pick_category() -> str:
    """Выбор случайно категории."""
    population = [c for c, _ in CATEGORIES]
    weights = [w for _, w in CATEGORIES]
    return random.choices(population, weights=weights, k=1)[0]


def _build_prompt() -> str:
    """Промпт."""
    category = _pick_category()
    prompt = (
        f"Напиши короткий пост (2–4 предложения) в таком ключе:\n{category}.\n\n"
        "Требования:\n"
        "- пост должен быть интересным и чему-то учить, а не звучать банально;\n"
        "- по существу, без длинных вступлений и воды;\n"
        "- не выдумывай конкретные даты, имена и события; если не уверен в факте, "
        "формулируй общее и без ложной точности;\n"
        "- это пост для практикующих йогу, которые хотят узнавать новое.\n\n"
        "В самой последней строке укажи одну короткую тему на русском для ссылки "
        "«читать подробнее» (название асаны, имя йогина, санскритский термин и т.п.) "
        "строго в формате:\nТЕРМИН: <тема>\n"
        "Если тема чисто философская и подходящего термина нет — напиши: ТЕРМИН: -"
    )
    return prompt


async def _generate_wisdom(config: Config, prompt: str) -> str:
    client = AsyncOpenAI(base_url=config.wisdom.url, api_key=config.wisdom.api_key)
    resp = await client.chat.completions.create(
        model=config.wisdom.model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=1.0,
        max_tokens=350,
        extra_body={"thinking": {"type": "disabled"}},  # отключаем рассуждения.
    )
    return (resp.choices[0].message.content or "").strip()


async def generate_wisdom(config: Config) -> str:
    """Сгенерировать текст мудрости."""
    prompt = _build_prompt()
    return await _generate_wisdom(config, prompt)


async def main():
    from pprint import pprint

    from app.config.config import load_config

    config = load_config(path_env=".env.dev", path_yaml="../../../config_dev.yaml")
    text = await generate_wisdom(config)
    pprint(text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
