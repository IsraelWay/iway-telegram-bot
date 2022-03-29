output.markdown("Проверка...")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}

if (record.getCellValueAsString("(check сотрудник) Консульская") != "Пройдена") {
    output.markdown("## Координатор не отметил, что консульская проверка Пройдена");
    return;
}

if (record.getCellValueAsString("(check) Договор") != "Подписан") {
    output.markdown("## Координатор не отметил, что договор подписан");
    return;
}

if (record.getCellValueAsString("target") == "masa" && record.getCellValueAsString("(check) Маса анкета") != "Заполнена") {
    output.markdown("## Координатор не отметил, что анкета масы заполнена");
    return;
}

if (record.getCellValueAsString("(check) Медбланк") != "Подписан и загружен") {
    output.markdown("## Координатор не отметил, что медбланк Подписан и загружен");
    return;
}

output.markdown(`## Перевести ${record.name} (${record.getCellValueAsString("Email")}) из ${record.getCellValueAsString("Город")}, ${record.getCellValueAsString("Страна (from Город)")} в статус * Pre-participant (Пре-Участник) * ?`)

let shouldContinue = await input.buttonsAsync(
    'Отправляем?',
    [
        {label: 'Отмена', value: 'cancel', variant: 'danger'},
        {label: 'Да, вперед', value: 'yes', variant: 'primary'},
    ],
);
if (shouldContinue === 'cancel') {
    output.clear();
    output.text('Отменено');
    return;
}

await leads.updateRecordAsync(record, {
    'Status': {
        name: "Pre-participant"
    },
});

output.clear();
output.markdown(`### ${record.getCellValueAsString("Info")} переведен в Pre-participant`);
