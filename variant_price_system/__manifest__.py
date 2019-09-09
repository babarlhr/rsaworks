# -*- coding: utf-8 -*-
{
    "name": "Advanced Variant Prices",
    "version": "12.0.1.0.22",
    "category": "Sales",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/advanced-variant-prices-378",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "sale"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_product.xml",
        "views/product_template_attribute_value.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "summary": "The tool to configure variant prices based on attributes coefficients and surpluses",
    "description": """
    In many industries product variant price strictly depends on its attribute values. Such dependency might be both cumulative (adds / subtracts some sum) and multiplicative (adds / subtracts certain percentage). This is the tool which let you quickly configure pricing in that way.

    Advanced formula to calculate variant price
    Different attributes coefficients for different product templates
    Compatibility with Odoo 12 product configurator
    Real-time pricing in any sale
    Advanced pricing as a base for Odoo pricelists
    # Pricing Formula
    <p style='font-size:18px;'>
The pricing formula is [ [(PRODUCT TEMPLATE PRICELIST PRICE + ATTRIBUTE 1 EXTRA PRICE) * (100+ATTRIBUTE 1 MULTIPLIER)/100 +  ATTRIBUTE 2 EXTRA PRICE] * [100+ATTRIBUTE 2 MULTIPLIER]/100 + ATTRIBUTE 3 EXTRA PRICE ] * ....
</p>
    # Price calculation example
    <ol>
    <li>Your product is "Ice Cream", which sale price is $5</li>
    <li>It has 2 attributes - "Flavour" and "Mode"</li>
    <li>The flavour may be "Chocolate", "Vanilla" or "Strawberry". While the first 2 do not influence costs, the latter make you put fresh fruits. That's why you decide to make a price extra of $1</li>
    <li>You have 2 ice cream modes: "Standard" and "Premium". The latter means you are using premium milk, which costs 20% more than ordinary one. Hence, you assign 20% multiplier to this attribute</li>
    <li>Since flavour doesn't influence mode at all, you decide <strong>to order attributes</strong> as "Mode, Flavour"</li>
    <li><i class="fa fa-arrow-right"></i> Then, the price of "Ice Crem, Premium, Strawberry" will be calculated as <strong>[($5 + 20%) + $1] = $7</strong></li>
    <li>Be cautious: if you decided <i>to order attributes in the opposite way</i> the price of "Ice Crem, Premium, Strawberry" will be  [($5 + $1) * (1+20%)] =$7,2</li>
    <li>Add a special extra for the product "Ice Cream, Premium, Strawberry" on its form - $2. Thus, the price would be $9</li>
</ol>
    # Special case: independent variant prices
    <p style='font-size:18px;'>Sometimes, variant prices don't have a strict correlation with template prices. In such a case there is a need to assign an own product price disregarding attributes and template core settings. The tool let you reach that goal. To configure independent price:</p>
<ul style='font-size:18px;'>
<li>Define a template price as zero</li>
<li>Do not assign coefficients for attributes, but you may define surpluses (e.g. a product has 2 attribute values, one of which has 5 Euro extra)</li>
<li>Make an own variant surplus as a final variant price (e.g. 100 Euro)</li>
<li>The tool would calculate a final variant price as: 0 + 5 + 0 + 100 = 105 Euro. It is fully independent from a template price.</li>
</ul>
    Configure price calculations on a template form
    Assign coefficients and surpluses per attribute values
    Variant might have an own extra price beside calculations
    Each product variant has a unique calculated price
    Variant price in Odoo 12 product configurator
    Even 'to create' and 'never created' attributes might influence pricing
    I faced the error: QWeb2: Template 'X' not found
    <div class="knowsystem_block_title_text">
            <div class="knowsystem_snippet_general" style="margin:0px auto 0px auto;width:100%;">
                <table align="center" cellspacing="0" cellpadding="0" border="0" class="knowsystem_table_styles" style="width:100%;background-color:transparent;border-collapse:separate;">
                    <tbody>
                        <tr>
                            <td width="100%" class="knowsystem_h_padding knowsystem_v_padding o_knowsystem_no_colorpicker" style="padding:20px;vertical-align:top;text-align:inherit;">
                                
                                <ol style="margin:0px 0 10px 0;list-style-type:decimal;"><li><p class="" style="margin:0px;">Restart your Odoo server and update the module</p></li><li><p class="" style="margin:0px;">Clean your browser cashe (Ctrl + Shift + R) or open Odoo in a private window.</p></li></ol></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    How should I install your app?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="line-height:120%;margin:0px 0px 10px 0px;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><ol style="margin:0px 0 10px 0;list-style-type:decimal;">
	<li><p style="margin:0px;line-height:120%;">Unzip source code of purchased tools in one of your Odoo
	add-ons directory</p>
	</li><li><p style="margin:0px;line-height:120%;">Re-start the Odoo server</p>
	</li><li><p style="margin:0px;line-height:120%;">Turn on the developer mode (technical settings)</p>
	</li><li><p style="margin:0px;line-height:120%;">Update the apps' list (the apps' menu)</p>
	</li><li><p style="margin:0px;line-height:120%;">Find the app and push the button 'Install'</p>
	</li><li><p style="margin:0px;line-height:120%;">Follow the guidelines on the app's page if those exist.</p>
</li></ol>
    May I buy your app from your company directly?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 10px 0px;">Sorry, but no. We distribute the
tools only through the <a href="https://apps.odoo.com/apps" style="text-decoration:none;color:rgb(13, 103, 89);background-color:transparent;">official Odoo apps store</a></p>
    Your tool has dependencies on other app(s). Should I purchase those?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Yes, all modules marked in
dependencies are absolutely required for a correct work of our tool.
Take into account that prices marked on the app page already includes
all necessary dependencies.&nbsp;&nbsp;</p>
    I noticed that your app has extra add-ons. May I purchase them afterwards?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Yes, sure. Take into account that Odoo
automatically adds all dependencies to a cart. You should exclude
previously purchased tools.</p>
    I would like to get a discount
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Regretfully, we do not have a
technical possibility to provide individual prices.</p>
    What are update policies of your tools?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">According to the current Odoo store
policies, by purchasing a tool you receive rights for all current and
all future versions of the tool.</p>
    How can I install your app on Odoo.sh?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 10px 0px;">As soon as you purchased the
app, the button 'Deploy on Odoo.sh' will appear on the app's page in
the Odoo store. Push this button and follow the instructions.</p>
<p style="margin:0px 0px 10px 0px;">Take into account that for paid
tools you need to have a private GIT repository linked to your
Odoo.sh projects</p>
    May I install the app on my Odoo Online (SaaS) database?
    <p style="margin:0px 0px 10px 0px;">No, third party apps can not be used on Odoo Online.</p>
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "96.0",
    "currency": "EUR",
}