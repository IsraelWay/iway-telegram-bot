let config = input.config();

let intExpenses = base.getTable("Internal expanses by group");
let expenses = base.getTable("Finance");
let expense = await expenses.selectRecordAsync(config.expanseId);
let groups = base.getTable("Группы");

if (!expense) {
  return;
}

// Delete all internal expanses
console.log("Exp: " + expense.getCellValueAsString("Summary"));
let intExp2Del = expense.getCellValue("Internal expanses by group");
if (intExp2Del) {
  console.log("To delete: " + intExp2Del);
  intExpenses.deleteRecordsAsync(intExp2Del.map((rec) => rec.id));
}

// Create new internal expanses
let intExp2Create = [];
for (let item of expense.getCellValue("Группы")) {
  let group = await groups.selectRecordAsync(item.id);
  if (!group) {
    console.log("Group is not found " + item.id)
    return;
  }

  let percent = group.getCellValue("Количество участников в группе") / expense.getCellValue("Количество всего участников");
  intExp2Create.push({
    fields: {
    "Группа": [{id: group.id}],
    "Трата на группу": expense.getCellValue("Amount (₪)") * percent,
    "Ссылка на трату": [{id:expense.id}]
  }})
}

await intExpenses.createRecordsAsync(intExp2Create);