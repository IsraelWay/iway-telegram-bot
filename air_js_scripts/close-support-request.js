let requests = base.getTable("EmailRequests");
let record = await input.recordAsync('',requests).catch()

if (!record) {
    output.markdown(`### Вопросу не найден`);
    return;
}

if (record.getCellValueAsString("Ответ")) {
    output.markdown(`### Вопросу уже отвечен`);
    return;
}

await requests.updateRecordAsync(record, {
    'Ответ': 'Беседа завершена',
});
output.markdown(`### Беседа завершена`);
