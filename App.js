import React, { Component } from 'react'
import jsQR from 'jsqr'

const { requestAnimationFrame } = global

class QRScan extends Component {
  constructor (props) {
    super(props)
    this.state = {
      output: "",
      notEnabled: true,
      loading: true,
      video: null
    }
  }

  componentDidMount () {
    const video = document.createElement('video')
    const canvasElement = document.getElementById('qrCanvas')
    const canvas = canvasElement.getContext('2d')

    this.setState({ video })

    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } }).then(function (stream) {
      video.srcObject = stream
      video.setAttribute('playsinline', true)
      video.play()
      requestAnimationFrame(tick)
    })

    const tick = () => {
      if (this.state.notEnabled) this.setState({ notEnabled: false })
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        if (this.state.loading) this.setState({ loading: false })
        canvasElement.height = video.videoHeight
        canvasElement.width = video.videoWidth
        canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height)
        var imageData = canvas.getImageData(0, 0, canvasElement.width, canvasElement.height)
        var code = jsQR(imageData.data, imageData.width, imageData.height, {
          inversionAttempts: 'dontInvert'
        })
        if (code) {
          this.setState({output : code.data})
          console.log(code.data)
          this.props.onFind(code.data)
        }
      }
      requestAnimationFrame(tick)
    }
  }

  componentWillUnmount () {
    this.state.video.pause()
  }

  render () {
    const {output} = this.state
    let message
    if (this.state.notEnabled) {
      message = <div><span role='img' aria-label='camera'>🎥</span> Unable to access video stream (please make sure you have a webcam enabled)</div>
    } else if (this.state.loading) {
      message = <div><span role='img' aria-label='time'>⌛</span> Loading video...</div>
    }

    return (
      <div>
        <form action = "http://localhost:5000/login" method = "post">
          <p> Generate an Email Verification Code </p>
          <p><input type = "text" name = "nm" placeholder = "Email" style={{width : 200}} required/></p>
          <p><input type = "submit" value = "submit" /></p>
        </form>
        { message }
        <canvas id='qrCanvas' />
        <form action = "http://localhost:5000/signOut" method = "post">
          <p> Sign Out a Laptop </p> 
          <p><input type = "text" name = "QR" value = {output} placeholder = "Scan Laptop QR Code" required/></p>
          <p><input type = "text" name = "email" placeholder = "Email" required/></p>
          <p><input type = "text" name = "code" placeholder = "Email Verification Code" required/></p>
          <p><input type = "submit" value = "submit" /></p>
        </form>
        <form action = "http://localhost:5000/return" method = "post">
          <p> Return a Laptop </p>
          <p> <input type = "text" name = "email" placeholder = "Email" /> </p>
          <p> <input type = "text" name = "code" placeholder = "Email Verification Code" /> </p>
          <p><input type = "submit" value = "submit" /></p>
        </form>
        <form action = "http://localhost:5000/admin" method = "post">
          <p> Admin </p>
          <p> <input type = "text" name = "code" placeholder = "Administrator Passcode" /> </p>
          <p><input type = "submit" value = "submit" /></p>
        </form>
        
      </div>
    )
  }
}

export default QRScan