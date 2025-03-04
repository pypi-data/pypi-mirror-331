"""
@Author: kang.yang
@Date: 2024/9/14 09:44
"""
from kytest.adr import Page, Elem


class AdrPage(Page):
    ad_btn = Elem(resourceId='com.qizhidao.clientapp:id/bottom_btn')
    my_tab = Elem(xpath='//android.widget.FrameLayout[4]')
    space_tab = Elem(text='科创空间')
    set_btn = Elem(resourceId='com.qizhidao.clientapp:id/me_top_bar_setting_iv')
    title = Elem(resourceId='com.qizhidao.clientapp:id/tv_actionbar_title')
    agree_text = Elem(resourceId='com.qizhidao.clientapp:id/agreement_tv_2')
    more_service = Elem(xpath='//*[@resource-id="com.qizhidao.clientapp:id/layout_top_content"]'
                       '/android.view.ViewGroup[3]/android.view.View[10]')
    page_title = Elem(resourceId='com.qizhidao.clientapp:id/tv_actionbar_title')

