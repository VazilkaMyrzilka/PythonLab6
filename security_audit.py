"""
Лабораторна робота № 6. Модуль 2.
Аудит безпеки мережевих портів, розрахунок коефіцієнта Жаккара
та частотний аналіз подій засобами collections.Counter.
Освітній компонент: Програмування на Python.
"""

from collections import Counter
import sys
import time

# Нормативний еталон мінімально необхідних привілеїв безпечної ролі додатку (Least Privilege Baseline)
ROLE_BASELINE_PRIVILEGES: frozenset[str] = frozenset({"SELECT", "INSERT", "UPDATE", "CONNECT"})


def audit_role_privileges(actual_privileges: set[str], baseline_privileges: frozenset[str]) -> dict:
    """
    Здійснює теоретико-множинний аудит відповідності прав ролі еталону:
    обчислює несанкціоновані (надлишкові) привілеї, відсутні обов'язкові привілеї та індекс Жаккара.
    """
    # 1. Несанкціоновані надлишкові привілеї (A \ B)
    unauthorized_privileges = actual_privileges.difference(baseline_privileges)

    # 2. Відсутні обов'язкові привілеї (B \ A)
    missing_required_privileges = baseline_privileges.difference(actual_privileges)

    # 3. Спільні легітимні привілеї (A ∩ B)
    compliant_privileges = actual_privileges.intersection(baseline_privileges)

    # 4. Об'єднання всіх унікальних привілеїв аудиту (A ∪ B)
    total_evaluated_privileges = actual_privileges.union(baseline_privileges)

    # 5. Розрахунок коефіцієнта подібності Жаккара J(A, B) = |A ∩ B| / |A ∪ B|
    if not total_evaluated_privileges:
        jaccard_index = 1.0
    else:
        jaccard_index = len(compliant_privileges) / len(total_evaluated_privileges)

    return {
        "compliant_privileges": compliant_privileges,
        "unauthorized_privileges": unauthorized_privileges,
        "missing_required_privileges": missing_required_privileges,
        "jaccard_similarity": jaccard_index,
    }


def analyze_security_event_frequency(event_stream: list[str]) -> Counter:
    """
    Здійснює частотний аналіз подій блокувань (Counter Lock) та помилок автентифікації/авторизації
    за допомогою структури collections.Counter.
    """
    event_counter = Counter(event_stream)
    return event_counter


def main() -> None:
    """Головна точка входу модуля аудиту безпеки СУБД."""
    t_start = time.perf_counter()

    print("=" * 80)
    print(f"{'АУДИТ ПРИВІЛЕЇВ РОЛЕЙ СУБД ТА ЧАСТОТНИЙ АНАЛІЗ ПОДІЙ БЛОКУВАНЬ (COUNTER LOCK)':^95}")
    print("=" * 80)

    # Фактичні привілеї проблемної ролі в СУБД (з аномальними DELETE, DROP, EXECUTE)
    actual_role_privileges = {"SELECT", "INSERT", "UPDATE", "CONNECT", "DELETE", "DROP", "EXECUTE"}

    print(f"Еталон найменших привілеїв (Baseline): {sorted(ROLE_BASELINE_PRIVILEGES)}")
    print(f"Фактичний профіль привілеїв ролі:     {sorted(actual_role_privileges)}")
    print("-" * 80)

    # 1. Теоретико-множинний аналіз
    audit_results = audit_role_privileges(actual_role_privileges, ROLE_BASELINE_PRIVILEGES)

    print(f"{'РЕЗУЛЬТАТИ ВАЛІДАЦІЇ ПРИВІЛЕЇВ РОЛІ':^95}")
    print(f"  Легітимні спільні привілеї (A ∩ B):      {sorted(audit_results['compliant_privileges'])}")
    print(f"  НЕБЕЗПЕЧНІ надлишкові права (A \\ B):     {sorted(audit_results['unauthorized_privileges'])}")
    print(f"  ВІДСУТНІ обов'язкові права (B \\ A):     {sorted(audit_results['missing_required_privileges'])}")
    print(f"  Коефіцієнт відповідності Жаккара:        {audit_results['jaccard_similarity'] * 100:.2f}% (J = {audit_results['jaccard_similarity']:.4f})")
    print("-" * 80)

    # 2. Частотний аналіз подій блокувань (Counter Lock / помилки доступу в логах СУБД)
    db_lock_events = [
        "RowLock_Timeout", "Deadlock_Detected", "RowLock_Timeout", "Auth_Failed",
        "RowLock_Timeout", "Deadlock_Detected", "ExclusiveLock_Blocked", "RowLock_Timeout",
        "Deadlock_Detected", "Auth_Failed", "RowLock_Timeout", "RowLock_Timeout",
    ]

    freq_stats = analyze_security_event_frequency(db_lock_events)

    print(f"{'ЧАСТОТНИЙ АНАЛІЗ ПОДІЙ БЛОКУВАНЬ ТА ПОМИЛОК (COUNTER LOCK TOP EVENTS)':^95}")
    print(f"| {'Ранг':^6} | {'Тип події блокування / помилки':^38} | {'Кількість фіксацій':^20} | {'Частка від усіх':^18} |")
    print("-" * 80)

    total_events = len(db_lock_events)
    for rank, (event, count) in enumerate(freq_stats.most_common(3), start=1):
        percentage = (count / total_events) * 100.0
        print(f"| {rank:^6d} | {event:^38} | {count:^20d} | {percentage:^17.2f}% |")

    print("=" * 80 + "\n")
    t_elapsed = time.perf_counter() - t_start
    print(f"Час виконання модуля аудиту безпеки СУБД: {t_elapsed * 1000:.3f} мс\n")


if __name__ == "__main__":
    main()