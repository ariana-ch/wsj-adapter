#!/usr/bin/env python3
"""
Debug script to see what content is being extracted for each headline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from wsj_adapter.wsj_adapter import extract_newsletter_content
from bs4 import BeautifulSoup

# Sample HTML from the user's example (truncated for brevity)
sample_html = '''
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse!important;" width="100%">
<tr>
<td class="email-body__space" style="padding-top:0;padding-bottom:16px;padding-right:0;padding-left:0;" valign="top">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse!important;" width="100%">
<tr>
<td valign="top">
<h1 style="color:#333;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif!important;font-size:24px;font-weight:400;letter-spacing:0;line-height:32px;margin-top:0;margin-bottom:0;margin-right:0;margin-left:0;">Supply Chain Strategies</h1>
</td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td valign="top">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse!important;" width="100%">
<tr>
<td class="email-body__article" style="color:#333;font-family:Georgia,Times,'Times New Roman',serif!important;font-size:16px;line-height:24px;" valign="top">
<p style="margin-top:0;margin-bottom:18px;margin-right:0;margin-left:0;">
<strong>The Covid-19 recovery in Europe is raising new healthcare supply-chain concerns across the continent.</strong> European countries are reporting shortages of amoxicillin, cephalosporins and other widely used <a href="https://web.archive.org/web/20221212225513/https://logistics.createsend1.com/t/d-l-zjkchd-l-x/" style="color:#0080c3;font-weight:400;text-decoration:underline;">antibiotics as demand rises and manufacturers grapple with shortfalls of ingredients and key supplies</a>. The WSJ's Cecilia Butini reports some materials are being held up because China's Covid restrictions have interrupted output and deliveries and that rising energy costs have made energy-intensive production difficult to maintain. Manufacturer <strong>Sandoz </strong>says it simply can't get all the screw caps and other components it needs. A major factor is that demand for antibiotics has rebounded strongly as more 
illnesses have coursed through populations following the lifting of Covid restrictions. It's a reminder that volatile turns in demand and supply that have marked the pandemic are still undercutting some sectors. For now, healthcare groups are trying to stretch supplies until they reach some equilibrium.</p>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td class="email-body__space" style="padding-top:0;padding-bottom:16px;padding-right:0;padding-left:0;" valign="top">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse!important;" width="100%">
<tr>
<td valign="top">
<h1 style="color:#333;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif!important;font-size:24px;font-weight:400;letter-spacing:0;line-height:32px;margin-top:0;margin-bottom:0;margin-right:0;margin-left:0;">Number of the Day</h1>
</td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td valign="top">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse!important;" width="100%">
<tr>
<td class="email-body__box" style="padding-top:4px;padding-bottom:20px;padding-right:0;padding-left:0;">
<table bgcolor="#F4F4F4" border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse!important;" width="100%">
<tr>
<td align="center" class="big-num__num sans" style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif!important;font-size:72px;font-weight:400;line-height:50px;padding-top:30px;padding-bottom:12px;padding-right:20px;padding-left:20px;" valign="top">
1,954,179
</td>
</tr>
<tr>
<td align="center" class="big-num__txt" style="padding-top:0;padding-bottom:2px;padding-right:20px;padding-left:20px;" valign="top">
<p style="margin-top:0;margin-bottom:18px;margin-right:0;margin-left:0;">
	Overall U.S. container imports in November, in 20-foot container equivalent units, down 12% from October and 19.4% year-over-year, according to Descartes Datamyne.</p>
</td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td class="email-body__space" style="padding-top:0;padding-bottom:16px;padding-right:0;padding-left:0;" valign="top">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse!important;" width="100%">
<tr>
<td valign="top">
<h1 style="color:#333;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif!important;font-size:24px;font-weight:400;letter-spacing:0;line-height:32px;margin-top:0;margin-bottom:0;margin-right:0;margin-left:0;">In Other News</h1>
</td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td valign="top">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse!important;" width="100%">
<tr>
<td class="email-body__article" style="color:#333;font-family:Georgia,Times,'Times New Roman',serif!important;font-size:16px;line-height:24px;" valign="top">
<p style="margin-top:0;margin-bottom:18px;margin-right:0;margin-left:0;">
	A.P. Moeller-Maersk said <a href="https://web.archive.org/web/20221212225513/https://logistics.createsend1.com/t/d-l-zjkchd-l-c/" style="color:#0080c3;font-weight:400;text-decoration:underline;">Vincent Clerc will replace Soren Skou as chief executive officer</a> on Jan. 1, 2023. (Dow Jones Newswires)</p>
<p style="margin-top:0;margin-bottom:18px;margin-right:0;margin-left:0;">
	U.S. supplier price <a href="https://web.archive.org/web/20221212225513/https://logistics.createsend1.com/t/d-l-zjkchd-l-q/" style="color:#0080c3;font-weight:400;text-decoration:underline;">increases eased</a> in November. (WSJ)</p>
<p style="margin-top:0;margin-bottom:18px;margin-right:0;margin-left:0;">
	Industrial metals prices are <a href="https://web.archive.org/web/20221212225513/https://logistics.createsend1.com/t/d-l-zjkchd-l-a/" style="color:#0080c3;font-weight:400;text-decoration:underline;">rallying on signs</a> that China will reopen its economy. (WSJ)</p>
</td>
</tr>
</table>
</td>
</tr>
</table>
'''

def debug_extraction():
    """Debug the extraction process"""
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    # Find all h1 elements
    h1_elements = soup.find_all('h1')
    print(f"Found {len(h1_elements)} h1 elements:")
    
    for i, h1 in enumerate(h1_elements, 1):
        headline = h1.get_text(strip=True)
        print(f"\n{i}. Headline: '{headline}'")
        
        # Try to find content for this headline
        current_element = h1
        content_found = False
        
        while current_element and not content_found:
            # Look for email-body__article
            next_article_td = current_element.find_next('td', class_=lambda x: x and 'email-body__article' in x)
            if next_article_td:
                print(f"   Found email-body__article td")
                content_text = next_article_td.get_text(strip=True)
                print(f"   Content preview: {content_text[:100]}...")
                content_found = True
                break
            
            # Look for big-num__txt
            next_num_td = current_element.find_next('td', class_=lambda x: x and 'big-num__txt' in x)
            if next_num_td:
                print(f"   Found big-num__txt td")
                content_text = next_num_td.get_text(strip=True)
                print(f"   Content preview: {content_text[:100]}...")
                content_found = True
                break
            
            current_element = current_element.parent
            if not current_element or current_element.name == 'body':
                break
        
        if not content_found:
            print(f"   No content found for this headline")

if __name__ == "__main__":
    debug_extraction() 