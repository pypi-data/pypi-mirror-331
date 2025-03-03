import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import add_dummy_feature
import matplotlib.pyplot as plt
from matplotlib import collections
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def _mockSingleXY():
    np.random.seed(42)
    m = 100
    X = 2 * np.random.rand(m)
    Y = 4 + 3 * X + np.random.randn(m)
    return X, Y


def _mockMultiXY():
    X = np.array([[1, 2], [2, 4], [3, 5], [4, 4], [5, 5]])
    Y = np.array([3, 5, 7, 8, 10])
    return X, Y


def _getColors(num):
    return list(map(lambda x: tuple([0.2 + x / num * 0.8, 0, 0]), range(num)))


def _getLines(theta0, theta1, x_start, x_end):
    y1 = []
    y2 = []
    points = []
    # 是原生python数组，只能用这种方式！！
    for i in range(len(theta0)):
        y1.append(theta0[i] + x_start * theta1[i])
        y2.append(theta0[i] + x_end * theta1[i])
    for i in range(len(theta0)):
        points.append([tuple([x_start, y1[i]]), tuple([x_end, y2[i]])])
    return points


def linreg_single_normal_equation(X, Y):
    # 一维变二维
    X_b = X.reshape(-1, 1)
    X_b = add_dummy_feature(X_b)
    return np.linalg.inv(X_b.T @ X_b) @ (X_b.T) @ Y


def example_linreg_single_normal_equation():
    X, Y = _mockSingleXY()
    ret = linreg_single_normal_equation(X, Y)
    print("theta参数为:", ret)

def linreg_multi_normal_equation(X, Y):
    X_b = add_dummy_feature(X)
    return np.linalg.inv(X_b.T @ X_b) @ (X_b.T) @ Y


def example_linreg_multi_normal_equation():
    X, Y = _mockMultiXY()
    ret = linreg_multi_normal_equation(X, Y)
    print("theta参数为:", ret)


def linreg_single_sklearn(X, Y):
    lin_reg = LinearRegression()
    # 一维变二维
    X_b = X.reshape(-1, 1)
    lin_reg.fit(X_b, Y)
    return (lin_reg.intercept_, lin_reg.coef_)


def example_linreg_single_sklearn():
    X, Y = _mockSingleXY()
    ret = linreg_single_sklearn(X, Y)
    print("theta参数为:", ret)


def linreg_multi_sklearn(X,y):
    # deepseek给的demo，格式很规范，后续按照这个模版来开发
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"训练集长度:{len(y_train)},测试集长度:{len(y_test)}")
    # 创建线性回归模型
    model = LinearRegression()
    # 训练模型
    model.fit(X_train, y_train)
    print(f'训练结果   模型系数:{model.coef_},截距:{model.intercept_}')
    # 使用测试集进行预测
    y_pred = model.predict(X_test)
    # 计算均方误差和R^2分数
    mse = mean_squared_error(y_test, y_pred)
    print(f"预测结果   真实值: {y_test},预测值:{y_pred},误差mse:{mse}")
 
    
    
def example_linreg_multi_sklearn():
    X, Y = _mockMultiXY()
    linreg_multi_sklearn(X, Y)


def linreg_single_bgd(X, Y, **kwargs):
    alpha = kwargs.get("alpha", 0.1)
    # 从y=0开始出发
    theta0 = 0
    theta1 = 0
    THETA0 = []
    THETA1 = []
    # 随意数据
    tmp0 = 1.0
    tmp1 = 1.0
    cnt = 0
    deviation = kwargs.get("deviation", 1e-6)
    while abs(tmp0) > deviation and abs(tmp1) > deviation:
        tmp0 = 1 / len(X) * np.sum(theta0 + theta1 * X - Y)
        tmp1 = 1 / len(Y) * np.sum((theta0 + theta1 * X - Y) * X)
        theta0 = theta0 - alpha * tmp0
        theta1 = theta1 - alpha * tmp1
        THETA0.append(float(theta0))
        THETA1.append(float(theta1))
        cnt += 1
        print("第", cnt, "次迭代，系数分别为", theta0, theta1)
    print("最终结果为：", theta0, theta1)
    return THETA0, THETA1


def example_linreg_single_bgd():
    X, Y = _mockSingleXY()
    linreg_single_bgd(X, Y)


def plot_linreg_single_bgd(X, Y, **kwargs):
    if kwargs.get("axis") is None:
        Xmax = np.max(X)
        Xmin = np.min(X)
        Ymax = np.max(Y)
        Ymin = np.min(Y)
        axis = [
            Xmin - (Xmax - Xmin) / 5,
            Xmax + (Xmax - Xmin) / 5,
            Ymin - (Ymax - Ymin) / 5,
            Ymax + (Ymax - Ymin) / 5,
        ]
        print("axis:", axis)
    else:
        axis = kwargs.get("axis")
    # 获取参数
    theta0, theta1 = linreg_single_bgd(X, Y, **kwargs)
    lines = _getLines(theta0, theta1, axis[0], axis[1])
    fig, axes = plt.subplots(1, 1)
    axes.add_collection(
        collections.LineCollection(lines, colors=_getColors(len(lines)))
    )

    plt.plot(X, Y, "b.")
    plt.xlabel("x")
    plt.ylabel("y", rotation=0)
    plt.axis(axis)
    plt.show()


def example_plot_linreg_single_bgd():
    X, Y = _mockSingleXY()
    plot_linreg_single_bgd(X, Y, alpha=0.1, deviation=1e-6)


if __name__ == "__main__":
    # example_linreg_single_normal_equation()
    # example_linreg_single_bgd()
    # example_plot_linreg_single_bgd()
    # example_linreg_single_sklearn()
    example_linreg_multi_sklearn()
    example_linreg_multi_normal_equation()