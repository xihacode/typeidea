from django.contrib.admin import AdminSite


class CustomSite(AdminSite):
    """实现自定义的site,AdminSite提供首页、登陆页、密码修改等页面的重载接口"""
    site_header = "LiuKun"
    site_title = "LiuKun 管理后台"
    index_title = "首页"


custom_site = CustomSite(name='cus_admin')
