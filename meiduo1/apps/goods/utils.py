
def get_breadcrumb(category):
    breadcrumb={
        "cat1":'',
        "cat2":'',
        "cat3":'',

    }
    # a = category.subs
    if category.parent is None:
        breadcrumb['cat1']=category
    elif category.subs.count() == 0:
        breadcrumb['cat3']=category
        breadcrumb['cat2']=category.parent
        breadcrumb['cat1']=category.parent.parent
    else:
        breadcrumb['cat2']=category
        breadcrumb['cat1']=category.parent
    return breadcrumb