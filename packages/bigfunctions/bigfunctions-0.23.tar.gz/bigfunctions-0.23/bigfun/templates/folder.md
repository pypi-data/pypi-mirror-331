---
{{ frontmatter }}
---

{% set path_parts = folder.split('/') %}

{% if path_parts|length > 1 %}

<div class="breadcrumb" markdown>

{% for part in path_parts -%}
- [{{ part }}]({{ '../' * loop.revindex0 }}README.md){% if not loop.last %}<span style="margin: 0 20px">❯</span>{% endif %}
{% endfor -%}

</div>

{% endif %}



{{ readme }}


{% if subfolders %}

## Function Categories

<div class="grid cards  " markdown>

{% for subfolder in subfolders -%}

-   ### [{{ subfolder.title }}]({{ subfolder.name }}/README.md)

    {% if subfolder.content -%}
    ---

    {{ subfolder.content | indent(4) }}
    {% endif %}

{% endfor %}

{% endif %}



{% if bigfunctions %}

## Functions

<div class="functions-table" markdown>

| Function | Short Description |
|------|---------|
{% for bigfunction in bigfunctions if not bigfunction.hide_in_doc -%}
| [<code>{{ bigfunction.name }}</code>]({{ '../' * depth }}{{ bigfunction.name }}.md) | {{ bigfunction.short_description }} |
{% endfor -%}

</div>

{% endif %}
