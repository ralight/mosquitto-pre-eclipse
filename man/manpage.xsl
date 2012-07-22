<!-- Set parameters for manpage xsl -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:import href="/usr/share/xml/docbook/stylesheet/docbook-xsl/manpages/docbook.xsl"/>
	<!-- Don't display notes list of link urls. -->
	<xsl:param name="man.endnotes.list.enabled">0</xsl:param>
	<xsl:param name="man.endnotes.are.numbered">0</xsl:param>
	<!-- But if we do, set a base url for the relative links. -->
	<xsl:param name="man.base.url.for.relative.links">http://mosquitto.org/man/</xsl:param>
</xsl:stylesheet>
