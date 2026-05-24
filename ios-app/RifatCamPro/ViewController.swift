import UIKit

class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(red: 1, green: 51/255, blue: 102/255, alpha: 1)

        let label = UILabel()
        label.text = "RifatCam Pro"
        label.textColor = .white
        label.font = UIFont.systemFont(ofSize: 32, weight: .bold)
        label.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(label)
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])

        let sublabel = UILabel()
        sublabel.text = "App is running!"
        sublabel.textColor = UIColor.white.withAlphaComponent(0.8)
        sublabel.font = UIFont.systemFont(ofSize: 16)
        sublabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(sublabel)
        NSLayoutConstraint.activate([
            sublabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            sublabel.topAnchor.constraint(equalTo: label.bottomAnchor, constant: 12)
        ])

        print("[VC] viewDidLoad complete")
    }
}
