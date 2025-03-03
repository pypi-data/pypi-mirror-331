import matplotlib

matplotlib.use("TkAgg")  # todo
import matplotlib.pyplot as plt

max_iter_2_recall = {
    2: {"average_recall": {"2": 0.71, "5": 0.74}, "token_usage": 160431},
    3: {"average_recall": {"2": 0.76, "5": 0.795}, "token_usage": 241738},
    4: {"average_recall": {"2": 0.81, "5": 0.895}, "token_usage": 329078},
    5: {"average_recall": {"2": 0.795, "5": 0.905}, "token_usage": 380528},
    6: {"average_recall": {"2": 0.825, "5": 0.96}, "token_usage": 493762},
    7: {"average_recall": {"2": 0.835, "5": 0.94}, "token_usage": 552305},
}

naive_rag_recall = {"2": 0.56, "5": 0.685}

# 准备数据
max_iters = list(max_iter_2_recall.keys())
recalls_at_2 = [max_iter_2_recall[i]["average_recall"]["2"] for i in max_iters]
recalls_at_5 = [max_iter_2_recall[i]["average_recall"]["5"] for i in max_iters]
recall_2_usage = [max_iter_2_recall[i]["token_usage"] for i in max_iters]

# 绘制图形
plt.figure(figsize=(10, 6))

plt.plot(max_iters, recalls_at_2, marker="o", color="blue", label="Deep Searcher Recall@2")
plt.plot(max_iters, recalls_at_5, marker="s", color="red", label="Deep Searcher Recall@5")

# 画naive rag recall的两条虚线
plt.plot(
    max_iters,
    [naive_rag_recall["2"]] * len(max_iters),
    color="blue",
    linestyle="--",
    label="Naive RAG Recall@2",
)
plt.plot(
    max_iters,
    [naive_rag_recall["5"]] * len(max_iters),
    color="red",
    linestyle="--",
    label="Naive RAG Recall@5",
)

# 添加标题和坐标轴标签
plt.title("Max Iterations vs Recall")
plt.xticks(max_iters)
plt.xlabel("Max Iterations")
plt.ylabel("Recall")

# 显示图例
plt.legend()

# 展示图表
plt.grid(True)
# plt.show()
plt.savefig("max_iter_vs_recall.png")

plt.figure(figsize=(10, 6))

plt.plot(max_iters, recall_2_usage, marker="o", label="Token Usage")

# 添加标题和坐标轴标签
plt.title("Max Iterations vs Token Usage")
plt.xticks(max_iters)
plt.xlabel("Max Iterations")
plt.ylabel("Token Usage")

# 显示图例
plt.legend()

# 展示图表
plt.grid(True)
# plt.show()
plt.savefig("max_iter_vs_token_usage.png")
