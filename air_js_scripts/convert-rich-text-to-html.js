// Скрипт для Airtable: конвертация Rich Text в HTML
// Берет данные из поля Rich Text и сохраняет HTML в другое поле

// Server access
let creds = base.getTable('Techdata');
let host, token = null;
let servers = await creds.selectRecordsAsync();
for (let server of servers.records) {
   if (server.getCellValue("Active")) {
       host = server.getCellValueAsString("host");
       token = server.getCellValueAsString("token");
       break;
   }
}
if (!host || !token) {
    output.markdown("❌ Не задан доступ до сервера");
    return;
}
output.markdown("🔗 Connecting to: " + host);

// Получаем запись из таблицы "Шаблоны писем"
let templates = base.getTable("Шаблоны писем");
let record = await input.recordAsync('Выберите шаблон для конвертации', templates);

if (!record) {
    output.markdown("❌ Запись не выбрана");
    return;
}

// Настройки полей
let RICH_TEXT_FIELD = "Текст письма"; // Поле с Rich Text контентом
let HTML_FIELD = "Html"; // Поле для сохранения HTML

output.markdown(`### 🔄 Конвертация Rich Text в HTML`);
output.markdown(`📋 Таблица: **Шаблоны писем**`);
output.markdown(`📝 Запись: **${record.name || record.id}**`);
output.markdown(`📝 Поле Rich Text: **${RICH_TEXT_FIELD}**`);
output.markdown(`🌐 Поле HTML: **${HTML_FIELD}**`);

let richTextContent = record.getCellValue(RICH_TEXT_FIELD);
let existingHtml = record.getCellValueAsString(HTML_FIELD);

// Проверяем есть ли Rich Text контент
if (!richTextContent || richTextContent.trim() === "") {
    output.markdown(`\n❌ **Ошибка**: В поле "${RICH_TEXT_FIELD}" нет контента для конвертации`);
    return;
}

// Показываем что будем конвертировать
output.markdown(`\n📄 **Rich Text контент:**`);
let preview = richTextContent;
output.markdown(`\`\`\`\n${preview}\n\`\`\``);

// Предупреждаем если HTML уже есть
if (existingHtml && existingHtml.trim() !== "") {
    output.markdown(`\n⚠️ **Внимание**: В поле "${HTML_FIELD}" уже есть содержимое. Оно будет перезаписано.`);
}

try {
    output.markdown(`\n🔄 **Отправка на конвертацию...**`);

    // Отправляем запрос на конвертацию
    let response = await fetch(host + '/convert-airtable-rich-text', {
        method: 'POST',
        headers: {
            "Authorization": 'Bearer ' + token,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            rich_text: richTextContent
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    let data = await response.json();

    if (!data.result) {
        throw new Error(data.message || "Ошибка конвертации");
    }

    let htmlContent = data.payload.html;

    // Сохраняем HTML в поле
    await templates.updateRecordAsync(record.id, {
        [HTML_FIELD]: htmlContent
    });

    output.markdown(`\n✅ **Конвертация успешна!**`);

    // Показываем результат
    let htmlPreview = htmlContent;
    output.markdown(`\n🌐 **Результирующий HTML:**`);
    output.markdown(`\`\`\`html\n${htmlPreview}\n\`\`\``);

    output.markdown(`\n📊 **Статистика:**`);
    output.markdown(`- Исходный Rich Text: **${richTextContent.length}** символов`);
    output.markdown(`- Результирующий HTML: **${htmlContent.length}** символов`);
    output.markdown(`- Поле обновлено: **${HTML_FIELD}**`);

} catch (error) {
    output.markdown(`\n❌ **Ошибка конвертации**: ${error.message}`);
    output.markdown(`\nПроверьте:`);
    output.markdown(`- Доступность сервера: ${host}`);
    output.markdown(`- Корректность токена авторизации`);
    output.markdown(`- Содержимое поля "${RICH_TEXT_FIELD}"`);
}

output.markdown(`\n---\n### 📋 Как использовать скрипт:`);
output.markdown(`1. **Запустите скрипт** в Airtable`);
output.markdown(`2. **Выберите запись** из таблицы "Шаблоны писем"`);
output.markdown(`3. **Скрипт автоматически**:`);
output.markdown(`   - Возьмет содержимое поля "Rich Text"`);
output.markdown(`   - Отправит на сервер для конвертации`);
output.markdown(`   - Сохранит HTML в поле "HTML Content"`);

output.markdown(`\n### ✅ Поддерживаемые элементы Rich Text:`);
output.markdown(`- **Заголовки**: \`# ## ###\``);
output.markdown(`- **Списки**: \`- * 1. 2.\``);
output.markdown(`- **Чекбоксы**: \`[x] [ ]\``);
output.markdown(`- **Цитаты**: \`>\``);
output.markdown(`- **Ссылки**: \`[text](url)\``);
output.markdown(`- **Форматирование**: \`**bold** *italic* ~~strike~~\``);
output.markdown(`- **Код**: \`\`inline\`\` и \`\`\`блоки\`\`\``);

output.markdown(`\n### 📝 Пример Rich Text контента:`);
output.markdown(`\`\`\`
# Заголовок 1
> Цитата с [ссылкой](https://example.com)
- **Жирный** и *курсив* текст
- ~~Зачеркнутый~~ текст
[x] Выполненная задача
[ ] Невыполненная задача
\`\`\``);