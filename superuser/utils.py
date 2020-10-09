from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

from xhtml2pdf import pisa
from xhtml2pdf.config.httpconfig import httpConfig


def render_to_pdf(template_src, context_dict={}):
    order_id = context_dict['invoice_id']
    paid = context_dict['paid']
    if paid == False:
        output_file_src = settings.MEDIA_ROOT + '/invoices/' + 'invoice-' + str(order_id) + '.pdf'
    else:
        output_file_src = settings.MEDIA_ROOT + '/invoices/' + 'invoice-' + str(order_id) + '-paid.pdf'
    result_file = open(output_file_src, "w+b")
    httpConfig.save_keys('nosslcheck', True)
    template = get_template(template_src)
    html = template.render(context_dict)
    pdf = pisa.CreatePDF(
        html,
        dest=result_file
    )
    result_file.close()
    if not pdf.err:
        return output_file_src
    return None
