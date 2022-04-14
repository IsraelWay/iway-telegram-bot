function toName(string) {
  return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
}


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

output.markdown(`## Перевести ${record.name} (${record.getCellValueAsString("Email")}) из ${record.getCellValueAsString("Город")}, ${record.getCellValueAsString("Страна (from Город)")} в статус * Participant (Участник) * ?`)

let shouldContinue = await input.buttonsAsync(
    'Переводим?',
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
        name: "Participant"
    },
});

let participants = base.getTable("Участники");
let groups = base.getTable("Группы").getView("Active");
let group = await input.recordAsync("Выберите группу", groups);
if (!group) {
    output.markdown("## Группа не выбрана");
    return;
}

let resultId = null;
try {
    resultId = await participants.createRecordAsync({
        "Lead": [{id: record.id}],
        "Программа": [{id: record.getCellValue("Предпочитаемая программа")[0].id}],
        "Birthday": record.getCellValue("Дата рождения"),
        "Email":record.getCellValueAsString("Email"),
        "Gender": { name: record.getCellValueAsString("Пол") == "Мужской" ? "ז" : "נ"},
        "Группа": [{id: group.id}],
        "Имя участника": toName(record.getCellValueAsString("Имя как в загранпаспорте")) + ' ' + toName(record.getCellValueAsString("Фамилия как в загранпаспорте")),
        "Паспорт номер": record.getCellValueAsString("Номер загран. паспорта"),
        "Статус": {name: "Активный"},
    })
}
catch (e) {
    await leads.updateRecordAsync(record, {
        'Status': {
            name: "Participant"
        },
    });
    output.text("Ошибка");
    output.inspect(e);
}

if (!resultId) {
    output.clear();
    output.markdown(`### ${record.getCellValueAsString("Info")} переведен в Participant`);
    output.markdown(`### Но с созданием записи в таблице Участники была проблема`);
    return;
}

await leads.updateRecordAsync(record, {
    'Участник': [{
        id: resultId
    }],
});

output.clear();
output.markdown(`### ${record.getCellValueAsString("Info")} переведен в Participant`);
output.markdown(`### Запись в таблицу частники создана`);