import React, { useRef } from 'react';
import ScreenCapture from '../shared/ScreenCapture';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ScreenCaptureTest = () => {
  const captureRef = useRef(null);
  
  const handleCapture = (imageUrl) => {
    console.log('Capture effectuée:', imageUrl);
  };
  
  return (
    <div className="container mx-auto py-6 px-4">
      <div className="mb-4 flex justify-end">
        <ScreenCapture 
          targetRef={captureRef} 
          onCapture={handleCapture} 
        />
      </div>
      
      <div ref={captureRef} className="border rounded-md p-6 bg-white">
        <Card>
          <CardHeader>
            <CardTitle>Zone de capture d'écran</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Cette zone sera capturée lorsque vous cliquerez sur le bouton "Capturer".</p>
            <p className="mt-2">Vous pouvez y placer n'importe quel contenu que vous souhaitez capturer.</p>
            
            <div className="mt-4 p-4 bg-blue-50 rounded-md">
              <h3 className="font-medium mb-2">Exemple de document juridique</h3>
              <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam id dolor id nibh ultricies vehicula ut id elit.</p>
              <ul className="mt-2 list-disc list-inside">
                <li>Point important 1</li>
                <li>Point important 2</li>
                <li>Point important 3</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ScreenCaptureTest;
