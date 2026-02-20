<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" hasScaleBasedVisibilityFlag="0" version="3.4.14-Madeira" styleCategories="AllStyleCategories" minScale="1e+08">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <customproperties>
    <property value="false" key="WMSBackgroundLayer"/>
    <property value="false" key="WMSPublishDataSourceUrl"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property value="Value" key="identify/format"/>
  </customproperties>
  <pipe>
    <rasterrenderer opacity="0.7" classificationMin="10" type="singlebandpseudocolor" alphaBand="-1" band="1" classificationMax="30">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader colorRampType="INTERPOLATED" classificationMode="2" clip="0">
          <colorramp type="gradient" name="[source]">
            <prop v="43,131,186,255" k="color1"/>
            <prop v="215,25,28,255" k="color2"/>
            <prop v="0" k="discrete"/>
            <prop v="gradient" k="rampType"/>
            <prop v="0.25;171,221,164,255:0.5;255,255,191,255:0.75;253,174,97,255" k="stops"/>
          </colorramp>
          <item value="0a" label="0a" alpha="255" color="#2b83ba"/>
          <item value="1a" label="1a" alpha="255" color="#4495b6"/>
          <item value="2a" label="2a" alpha="255" color="#5ea7b1"/>
          <item value="3a" label="3a" alpha="255" color="#78b9ad"/>
          <item value="4a" label="4a" alpha="255" color="#91cba9"/>
          <item value="5a" label="5a" alpha="255" color="#abdda4"/>
          <item value="6a" label="6a" alpha="255" color="#bce4aa"/>
          <item value="7a" label="7a" alpha="255" color="#cdebaf"/>
          <item value="8a" label="8a" alpha="255" color="#def2b4"/>
          <item value="9a" label="9a" alpha="255" color="#eff9ba"/>
          <item value="10a" label="10a" alpha="255" color="#ffffbf"/>
          <item value="11a" label="11a" alpha="255" color="#ffefac"/>
          <item value="12a" label="12a" alpha="255" color="#ffdf9a"/>
          <item value="13a" label="13a" alpha="255" color="#fecf87"/>
          <item value="14a" label="14a" alpha="255" color="#febe74"/>
          <item value="15a" label="15a" alpha="255" color="#fdae61"/>
          <item value="16a" label="16a" alpha="255" color="#f69053"/>
          <item value="17a" label="17a" alpha="255" color="#ee7245"/>
          <item value="18a" label="18a" alpha="255" color="#e75437"/>
          <item value="19a" label="19a" alpha="255" color="#df3729"/>
          <item value="20a" label="20a" alpha="255" color="#d7191c"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast contrast="0" brightness="0"/>
    <huesaturation colorizeOn="0" colorizeGreen="128" colorizeStrength="100" colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeRed="255"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
