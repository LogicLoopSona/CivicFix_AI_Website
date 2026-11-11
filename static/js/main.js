function useMyLocation(){
  const button=document.getElementById('gpsButton');
  if(!navigator.geolocation){alert('Geolocation is not supported by this browser.');return;}
  button.disabled=true;button.textContent='Getting location...';
  navigator.geolocation.getCurrentPosition(pos=>{
    document.getElementById('latitude').value=pos.coords.latitude.toFixed(6);
    document.getElementById('longitude').value=pos.coords.longitude.toFixed(6);
    const location=document.getElementById('location');
    if(!location.value) location.value=`GPS: ${pos.coords.latitude.toFixed(5)}, ${pos.coords.longitude.toFixed(5)}`;
    button.disabled=false;button.textContent='✓ Location captured';
  },err=>{
    alert('Could not get location. Allow location permission and try again.');
    button.disabled=false;button.textContent='Use my location';
  },{enableHighAccuracy:true,timeout:10000});
}
document.addEventListener('DOMContentLoaded',()=>{
  const photo=document.getElementById('photo');
  if(photo) photo.addEventListener('change',()=>{
    const label=document.getElementById('fileName');
    if(label) label.textContent=photo.files.length?photo.files[0].name:'No file selected';
  });
});
