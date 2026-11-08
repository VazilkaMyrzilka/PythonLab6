"""
Лабораторна робота № 6. Модуль 1.
Інвентаризація мережевих ресурсів: маніпуляції словниками (dict),
безпечний доступ, оновлення та генерація інвертованих індексів.
Освітній компонент: Програмування на Python.
"""

import sys
import time


def create_initial_db_database() -> dict[str, dict]:
    """
    Створює первинний реєстр інстансів PostgreSQL корпоративного сегмента.
    Ключ: Instance_ID (str). Значення: словник параметрів (host, databases_set, active_users_set).
    """
    db_instances = {
        "pg-cluster-01": {
            "host": "192.168.1.10",
            "databases_set": {"users_db", "analytics_db", "orders_db"},
            "active_users_set": {"app_backend", "etl_service", "admin_dba"},
        },
        "pg-cluster-02": {
            "host": "192.168.1.11",
            "databases_set": {"billing_db", "audit_db"},
            "active_users_set": {"billing_app", "audit_bot"},
        },
        "pg-cluster-03": {
            "host": "192.168.1.22",
            "databases_set": {"crm_db", "reports_db"},
            "active_users_set": {"crm_backend", "reporter_svc"},
        },
    }
    return db_instances

def add_or_update_instance(db_database: dict, instance_id: str, instance_info: dict) -> None:    
    """
    Додає новий хост або оновлює параметри існуючого вузла
    за допомогою словникового методу update().
    """
    if instance_id in db_database:
        db_database[instance_id].update(instance_info)
    else:
        db_database[instance_id] = instance_info

def decommission_instance(db_database: dict, instance_id: str) -> dict:
    """
    Вилучає виведений з експлуатації хост за допомогою методу pop(),
    запобігаючи виникненню винятку KeyError.
    """
    removed_instance = db_database.pop(instance_id, None)
    if removed_instance is None:
        print(f"Попередження: Спроба видалення неіснуючого інстансу {instance_id}.")
    return removed_instance

def build_inverted_database_index(db_database: dict) -> dict[str, list[str]]:
    """
    Будує інвертований індекс баз даних за допомогою Dict Comprehension:
    відображає кожну унікальну базу даних на список ідентифікаторів інстансів (Instance_ID).
    """
    all_unique_dbs = set()
    for instance_data in db_database.values():
        all_unique_dbs.update(instance_data.get("databases_set", set()))

    inverted_index = {
        database: [
            inst_id
            for inst_id, data in db_database.items()
            if database in data.get("databases_set", set())
        ]
        for database in sorted(all_unique_dbs)
    }
    return inverted_index


def print_inventory_report(db_database: dict, inverted_index: dict) -> None:
    """Виводить на екран відформатований звіт інвентаризації СУБД PostgreSQL."""
    header_sep = "=" * 95
    sub_sep = "-" * 95

    print(header_sep)
    print(f"{'РЕЄСТР ІНСТАНСІВ POSTGRESQL ТА РОЗПОДІЛУ БАЗ ДАНИХ':^95}")
    print(header_sep)
    print(f"| {'Instance_ID':<15} | {'IP-хост':<15} | {'Бази даних (Databases_Set)':<32} | {'Активні користувачі':<22} |")
    print(sub_sep)

    for inst_id, data in sorted(db_database.items()):
        dbs_str = ", ".join(sorted(data.get("databases_set", set())))
        users_str = ", ".join(sorted(data.get("active_users_set", set())))
        
        host_str = data.get("host", "N/A")
        
        print(f"| {inst_id:<15} | {host_str:<15} | {dbs_str:<32} | {users_str:<22} |")

    print(header_sep)
    print(f"{'ІНВЕРТОВАНИЙ ІНДЕКС: БАЗА ДАНИХ -> СПИСОК ІНСТАНСІВ':^95}")
    print(sub_sep)
    for db_name, inst_list in inverted_index.items():
        inst_str = ", ".join(inst_list)
        print(f"  БД '{db_name:<15}' -> Інстанси: {inst_str}")
    print(header_sep + "\n")
def main() -> None:
    """Головна точка входу модуля інвентаризації мережевих ресурсів."""
    t_start = time.perf_counter()

    # 1. Створення бази інстансів
    db_db = create_initial_db_database()

    # 2. CRUD-модифікація: додавання шлюзу моніторингу
    new_monitoring_node = {
        "hostname": "192.168.1.1",
        "databases_set": {"analytics_db", "archive_db"},
        "active_users_set": {"etl_service", "archiver_bot"},
    }
    add_or_update_instance(db_db, "pg-cluster-replica", new_monitoring_node)

    # 3. Вилучення застарілого інстансу
    decommission_instance(db_db, "pg-cluster-03")

    # 4. Побудова інвертованого індексу
    db_index = build_inverted_database_index(db_db)

    # 5. Виведення звіту
    print_inventory_report(db_db, db_index)
    t_elapsed = time.perf_counter() - t_start
    print(f"Час виконання модуля інвентаризації: {t_elapsed * 1000:.3f} мс\n")


if __name__ == "__main__":
    main()