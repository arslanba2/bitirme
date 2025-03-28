from collections import defaultdict, deque


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.in_degree = defaultdict(int)
        self.duration = {}
        self.all_nodes = set()

    def add_task(self, task, duration, dependencies):
        """
        Operasyonu ve bağımlılıklarını ekler.
        :param task: Operasyon adı
        :param duration: Operasyon süresi
        :param dependencies: Bağımlı olduğu operasyonların listesi (düz liste olmalı)
        """
        self.all_nodes.add(task)
        self.duration[task] = duration

        # Eğer dependencies iç içe listeler içeriyorsa, düzleştir
        flat_dependencies = []
        for dep in dependencies:
            if isinstance(dep, list):  # Eğer dep bir listeyse, içindeki elemanları ekle
                flat_dependencies.extend(dep)
            else:  # Değilse, doğrudan ekle
                flat_dependencies.append(dep)

        for dep in flat_dependencies:
            self.all_nodes.add(dep)
            self.graph[dep].append(task)
            self.in_degree[task] += 1

        if task not in self.in_degree:
            self.in_degree[task] = 0

    def find_critical_operations(self):
        try:
            if not self.all_nodes:
                print("Kritik Yol Analizi: Grafta hiç düğüm yok.")
                return [], {}, {}

            # Her düğüm için süre tanımlandığından emin olalım
            for node in self.all_nodes:
                if node not in self.duration:
                    print(f"Uyarı: '{node}' düğümü için süre tanımlanmamış, 0.01 varsayılıyor.")
                    self.duration[node] = 0.01  # En az 0.01 süre

            # Topological sort
            queue = deque()
            in_degree_copy = self.in_degree.copy()  # Orijinali değiştirmemek için kopya oluştur

            for task in in_degree_copy:
                if in_degree_copy[task] == 0:
                    queue.append(task)

            topological_order = []
            while queue:
                node = queue.popleft()
                topological_order.append(node)

                for neighbor in self.graph[node]:
                    in_degree_copy[neighbor] -= 1
                    if in_degree_copy[neighbor] == 0:
                        queue.append(neighbor)

            # Topolojik sıralama tüm düğümleri içermiyor mu kontrol et
            if len(topological_order) != len(self.all_nodes):
                print("Uyarı: Topolojik sıralama tüm düğümleri içermiyor - döngü olabilir.")
                missing_nodes = self.all_nodes - set(topological_order)

                # Döngüsel bağımlılıkları çöz
                for node in missing_nodes:
                    # Bağımlılık varsa azalt
                    self.in_degree[node] = 0
                    topological_order.append(node)

            # Calculate earliest start and finish times
            earliest_start = {task: 0 for task in self.all_nodes}
            earliest_finish = {task: 0 for task in self.all_nodes}

            for task in topological_order:
                earliest_finish[task] = earliest_start[task] + self.duration[task]
                for neighbor in self.graph[task]:
                    earliest_start[neighbor] = max(earliest_start[neighbor], earliest_finish[task])

            # Calculate latest start and finish times
            max_finish_time = max(earliest_finish.values())
            latest_finish = {task: max_finish_time for task in self.all_nodes}
            latest_start = {task: max_finish_time - self.duration[task] for task in self.all_nodes}

            # Reverse topological order for latest calculations
            for task in reversed(topological_order):
                if not self.graph[task]:  # Eğer bağımlılık yoksa, latest_finish = max_finish_time
                    latest_finish[task] = max_finish_time
                else:
                    min_successor_start = float('inf')
                    for neighbor in self.graph[task]:
                        min_successor_start = min(min_successor_start, latest_start[neighbor])
                    latest_finish[task] = min_successor_start

                latest_start[task] = latest_finish[task] - self.duration[task]

            # Identify critical operations
            critical_operations = []
            for task in topological_order:
                # Kritik yolu tespit etmek için slack hesapla
                slack = latest_start[task] - earliest_start[task]
                if abs(slack) < 0.01:  # Küçük bir epsilon değeri
                    critical_operations.append(task)

            return critical_operations, earliest_start, latest_finish

        except Exception as e:
            print(f"Kritik Yol Analizi Hatası: {e}")
            import traceback
            traceback.print_exc()
            return [], {}, {}


# Örnek kullanım
if __name__ == "__main__":
    g = Graph()
    g.add_task('A', 3, [])
    g.add_task('B', 2, ['A'])
    g.add_task('C', 4, ['A'])
    g.add_task('D', 1, ['B', 'C'])
    g.add_task('E', 2, ['C'])
    g.add_task('F', 3, ['D', 'E'])

    critical_operations, earliest_start, latest_finish = g.find_critical_operations()

    print("Kritik Operasyonlar:", critical_operations)
    print("En Erken Başlama Zamanları:", earliest_start)
    print("En Geç Tamamlanma Zamanları:", latest_finish)