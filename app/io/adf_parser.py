def parse_adf_to_text(adf):
    """Convierte ADF (Atlassian Document Format) a texto plano estructurado."""
    if not isinstance(adf, dict) or adf.get("type") != "doc":
        return ""

    def extract_text_from_content(content):
        """Extrae texto de bloques de contenido con estructura básica."""
        text = ""
        for node in content:
            t = node.get("type")
            inner = node.get("content", [])
            if t == "paragraph":
                line = "".join(i.get("text", "") for i in inner if i.get("type") == "text")
                text += line + "\n\n"
            elif t == "heading":
                level = node.get("attrs", {}).get("level", 2)
                header = "".join(i.get("text", "") for i in inner if i.get("type") == "text")
                text += "#" * level + " " + header + "\n\n"
            elif t == "bulletList":
                for li in node.get("content", []):
                    line = ""
                    for p in li.get("content", []):
                        line += "".join(i.get("text", "") for i in p.get("content", []) if i.get("type") == "text")
                    text += f"- {line}\n"
                text += "\n"
            elif t == "orderedList":
                count = 1
                for li in node.get("content", []):
                    line = ""
                    for p in li.get("content", []):
                        line += "".join(i.get("text", "") for i in p.get("content", []) if i.get("type") == "text")
                    text += f"{count}. {line}\n"
                    count += 1
                text += "\n"
            # Otros tipos pueden agregarse acá si querés soportar más
        return text

    return extract_text_from_content(adf.get("content", []))


# Ejemplo de uso (podés probar con un JSON de Jira real):
ejemplo_adf = {
    "type": "doc",
    "version": 1,
    "content": [
        {
            "type": "heading",
            "attrs": { "level": 2 },
            "content": [{ "type": "text", "text": "Expected behavior" }]
        },
        {
            "type": "paragraph",
            "content": [{ "type": "text", "text": "The user should see a confirmation." }]
        },
        {
            "type": "bulletList",
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{ "type": "text", "text": "Read-only view for Passenger" }]
                        }
                    ]
                },
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{ "type": "text", "text": "Editable by Lead Client" }]
                        }
                    ]
                }
            ]
        }
    ]
}

