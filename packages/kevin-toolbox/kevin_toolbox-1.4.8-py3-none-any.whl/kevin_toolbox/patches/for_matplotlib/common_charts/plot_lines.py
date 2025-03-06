import matplotlib.pyplot as plt
from kevin_toolbox.patches.for_matplotlib.color import generate_color_list
from kevin_toolbox.patches.for_matplotlib.common_charts.utils import save_plot, save_record, get_output_path
from kevin_toolbox.patches.for_matplotlib.variable import COMMON_CHARTS

__name = ":common_charts:plot_lines"


@COMMON_CHARTS.register(name=__name)
def plot_lines(data_s, title, x_name, x_ticklabels_name=None, output_dir=None, output_path=None, **kwargs):
    """
        绘制折线图

        参数：
            data_s:             <dict> 数据。
                                    形如 {<data_name>: <data list>, ...} 的字典
            title:              <str> 绘图标题，同时用于保存图片的文件名。
            x_name:             <str> 以哪个 data_name 作为 x 轴。
                                    其余数据视为需要被绘制的数据点。
                    例子： data_s={"step":[...], "acc_top1":[...], "acc_top3":[...]}
                        当 x_name="step" 时，将会以 step 为 x 轴绘制 acc_top1 和 acc_top3 的 bar 图。
            x_ticklabels_name:  <str or None> 若提供则表示 x 轴刻度标签对应的键名，用于替换默认的 x 轴刻度值。
            output_dir:         <str> 图片输出目录。
            output_path:        <str> 图片输出路径。
                        以上两个只需指定一个即可，同时指定时以后者为准。
                        当只有 output_dir 被指定时，将会以 title 作为图片名。
                        若同时不指定，则直接调用 plt.show() 显示图像，而不进行保存。
                        在保存为文件时，若文件名中存在路径不适宜的非法字符将会被进行替换。

        其他可选参数：
            dpi:                <int> 保存图像的分辨率。
                                    默认为 200。
            suffix:             <str> 图片保存后缀。
                                    目前支持的取值有 ".png", ".jpg", ".bmp"，默认为第一个。
            b_generate_record:  <boolean> 是否保存函数参数为档案。
                                    默认为 False，当设置为 True 时将会把函数参数保存成 [output_path].record.tar。
                                    后续可以使用 plot_from_record() 函数或者 Serializer_for_Registry_Execution 读取该档案，并进行修改和重新绘制。
                                    该参数仅在 output_dir 和 output_path 非 None 时起效。
            color_ls:           <list> 用于绘图的颜色列表，默认根据数据序列个数自动生成。
            marker_ls:          <list of str> 折线图上各数据点的标记。
            linestyle_ls:       <list of str> 线型。
                                    默认值为 '-'，表示直线。
    """
    line_nums = len(data_s) - 1
    paras = {
        "dpi": 200,
        "suffix": ".png",
        "b_generate_record": False,
        "color_ls": generate_color_list(nums=line_nums),
        "marker_ls": None,
        "linestyle_ls": '-',
    }
    paras.update(kwargs)
    for k, v in paras.items():
        if k.endswith("_ls") and not isinstance(v, (list, tuple)):
            paras[k] = [v] * line_nums
    assert line_nums == len(paras["color_ls"]) == len(paras["marker_ls"]) == len(paras["linestyle_ls"])
    #
    _output_path = get_output_path(output_path=output_path, output_dir=output_dir, title=title, **kwargs)
    save_record(_func=plot_lines, _name=__name,
                _output_path=_output_path if paras["b_generate_record"] else None,
                **paras)
    data_s = data_s.copy()

    plt.clf()
    #
    x_all_ls = data_s.pop(x_name)
    if x_ticklabels_name is not None:
        x_ticklabels = data_s.pop(x_ticklabels_name)
        assert len(x_all_ls) == len(x_ticklabels)
        plt.xticks(x_all_ls, x_ticklabels)
    data_s, temp = dict(), data_s
    for k, v_ls in temp.items():
        y_ls, x_ls = [], []
        for x, v in zip(x_all_ls, v_ls):
            if x is None or v is None:
                continue
            x_ls.append(x)
            y_ls.append(v)
        if len(x_ls) == 0:
            continue
        data_s[k] = (x_ls, y_ls)
    #
    for i, (k, (x_ls, y_ls)) in enumerate(data_s.items()):
        plt.plot(x_ls, y_ls, label=f'{k}', color=paras["color_ls"][i], marker=paras["marker_ls"][i],
                 linestyle=paras["linestyle_ls"][i])
    plt.xlabel(f'{x_name}')
    plt.ylabel('value')
    plt.title(f'{title}')
    # 显示图例
    plt.legend()

    save_plot(plt=plt, output_path=_output_path, dpi=paras["dpi"], suffix=paras["suffix"])
    return _output_path


if __name__ == '__main__':
    import os

    plot_lines(
        data_s={
            'a': [1, 2, 3, 4, 5],
            'b': [5, 4, 3, 2, 1],
            'c': [1, 2, 3, 4, 5]},
        title='test_plot_lines',
        x_name='a', output_dir=os.path.join(os.path.dirname(__file__), "temp")
    )
